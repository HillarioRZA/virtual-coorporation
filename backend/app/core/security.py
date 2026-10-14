"""
Zero-Trust Secret Vault Security Manager.
Mengelola enkripsi dan dekripsi kredensial produksi menggunakan AES-256-GCM authenticated encryption.
"""

import base64
import hashlib
import os
from typing import Any, Dict, List, Optional
import aiosqlite
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.core.logger import logger
from app.db.session import get_db_connection


def _derive_32byte_key(raw_key: str) -> bytes:
    """Menghasilkan kunci 32-byte untuk AES-256 melalui base64 decode atau SHA-256 hash."""
    try:
        decoded = base64.b64decode(raw_key)
        if len(decoded) == 32:
            return decoded
    except Exception:
        pass
    return hashlib.sha256(raw_key.encode("utf-8")).digest()


class SecretVaultManager:
    """Manajer enkripsi AES-256-GCM untuk kredensial sensitif produksi."""

    def __init__(self, master_key: Optional[str] = None, custom_db_path: Optional[str] = None) -> None:
        """Inisialisasi AESGCM cipher dengan master key aman.

        Args:
            master_key: Kunci enkripsi mentah opsional (fallback ke settings.VAULT_MASTER_KEY).
            custom_db_path: Path basis data SQLite khusus untuk testing.
        """
        raw_key = master_key or settings.VAULT_MASTER_KEY
        self.key_bytes = _derive_32byte_key(raw_key)
        self.aesgcm = AESGCM(self.key_bytes)
        self.db_path = custom_db_path

    def encrypt(self, plaintext: str) -> str:
        """Mengenkripsi teks plaintext menjadi string base64 (nonce 12-byte + ciphertext + tag).

        Args:
            plaintext: Teks sensitif mentah.

        Returns:
            String base64 terenkripsi.
        """
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        payload = nonce + ciphertext
        return base64.b64encode(payload).decode("utf-8")

    def decrypt(self, encrypted_b64: str) -> str:
        """Mendekripsi string base64 menjadi teks plaintext dan memvalidasi keutuhan data.

        Args:
            encrypted_b64: String base64 terenkripsi.

        Returns:
            Teks plaintext yang telah didekripsi.

        Raises:
            ValueError: Jika payload rusak atau autentikasi data gagal.
        """
        try:
            payload = base64.b64decode(encrypted_b64)
            if len(payload) < 28:
                raise ValueError("Payload ciphertext terlalu pendek.")
            nonce = payload[:12]
            ciphertext = payload[12:]
            decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted_bytes.decode("utf-8")
        except Exception as err:
            logger.error(f"Gagal mendekripsi payload vault: {err}")
            raise ValueError(f"Dekripsi gagal atau data telah dimodifikasi: {err}") from err

    async def store_secret(self, project_id: str, key_name: str, value: str) -> None:
        """Menyimpan kredensial terenkripsi ke tabel vault_secrets.

        Args:
            project_id: ID proyek sasaran.
            key_name: Nama kunci (misal: 'STRIPE_SECRET_KEY').
            value: Nilai kredensial plaintext.
        """
        encrypted_val = self.encrypt(value)
        try:
            async with get_db_connection(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT OR IGNORE INTO projects (id, name, stage, founder_idea)
                    VALUES (?, ?, 'PRODUCTION_HARDENING', '')
                    """,
                    (project_id, project_id),
                )
                await conn.execute(
                    """
                    INSERT INTO vault_secrets (project_id, secret_key_name, encrypted_value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(project_id, secret_key_name) DO UPDATE SET
                        encrypted_value = excluded.encrypted_value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (project_id, key_name, encrypted_val),
                )
                await conn.commit()
            logger.info(f"Kredensial [{key_name}] berhasil dienkripsi dan disimpan untuk project [{project_id}]")
        except aiosqlite.Error as err:
            logger.error(f"Gagal menyimpan secret [{key_name}]: {err}")
            raise

    async def get_secret(self, project_id: str, key_name: str) -> Optional[str]:
        """Mengambil dan mendekripsi satu kredensial dari tabel vault_secrets.

        Args:
            project_id: ID proyek sasaran.
            key_name: Nama kunci kredensial.

        Returns:
            Nilai plaintext terdekripsi atau None jika tidak ditemukan.
        """
        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(
                    "SELECT encrypted_value FROM vault_secrets WHERE project_id = ? AND secret_key_name = ?",
                    (project_id, key_name),
                )
                row = await cursor.fetchone()
                if not row:
                    return None
                return self.decrypt(row["encrypted_value"])
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil secret [{key_name}]: {err}")
            raise

    async def list_secret_keys(self, project_id: str) -> List[str]:
        """Mengambil daftar nama kunci kredensial tanpa mengekspos nilainya.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            Daftar nama kunci kredensial yang tersimpan.
        """
        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(
                    "SELECT secret_key_name FROM vault_secrets WHERE project_id = ? ORDER BY secret_key_name ASC",
                    (project_id,),
                )
                rows = await cursor.fetchall()
                return [row["secret_key_name"] for row in rows]
        except aiosqlite.Error as err:
            logger.error(f"Gagal membaca daftar secret keys: {err}")
            raise

    async def get_all_decrypted(self, project_id: str) -> Dict[str, str]:
        """Mengambil dan mendekripsi seluruh kredensial untuk deployment kontainer produksi.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            Dictionary seluruh key-value kredensial terdekripsi.
        """
        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(
                    "SELECT secret_key_name, encrypted_value FROM vault_secrets WHERE project_id = ?",
                    (project_id,),
                )
                rows = await cursor.fetchall()
            
            result: Dict[str, str] = {}
            for row in rows:
                try:
                    result[row["secret_key_name"]] = self.decrypt(row["encrypted_value"])
                except Exception as dec_err:
                    logger.warning(f"Melewati key [{row['secret_key_name']}]: {dec_err}")
            return result
        except aiosqlite.Error as err:
            logger.error(f"Gagal memuat seluruh decrypted secrets: {err}")
            raise
