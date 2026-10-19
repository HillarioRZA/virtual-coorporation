"""
Secret Vault API Router.
Menangani penyimpanan terenkripsi dan inspeksi kunci kredensial produksi pada Stage-Gate 3.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.security import SecretVaultManager
from app.engine.memory.memory import MemoryManager

router = APIRouter(prefix="/projects", tags=["Secret Vault"])


class StoreSecretsRequest(BaseModel):
    """Payload penyimpanan kredensial rahasia ke Secret Vault."""

    secrets: Dict[str, str] = Field(
        ...,
        min_length=1,
        description="Dictionary pasangan key-value kredensial produksi (e.g. STRIPE_SECRET_KEY).",
    )


@router.post("/{project_id}/vault/secrets", status_code=status.HTTP_200_OK)
async def store_project_secrets(project_id: str, payload: StoreSecretsRequest) -> Dict[str, Any]:
    """Menyimpan kredensial produksi terenkripsi AES-256-GCM ke dalam Secret Vault."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Vault reject: Proyek [{project_id}] tidak ditemukan.")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    vault = SecretVaultManager()
    try:
        count = 0
        for key_name, secret_val in payload.secrets.items():
            if key_name and secret_val:
                await vault.store_secret(project_id, key_name.strip(), secret_val.strip())
                count += 1

        # Catat event audit penyimpanan vault ke blackboard (tanpa mengekspos plaintext)
        await mem.log_event(
            project_id=project_id,
            stage=state.stage,
            sender_role="CEO",
            recipient_role="DEVSECOPS",
            event_type="VAULT_SECRETS_INJECTED",
            content=f"Founder menginjeksi {count} kredensial produksi terenkripsi ke Secret Vault.",
        )

        return {
            "status": "success",
            "message": f"{count} kredensial berhasil dienkripsi dan disimpan di Secret Vault.",
        }
    except Exception as err:
        logger.error(f"Gagal menyimpan kredensial vault: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal memproses kredensial vault: {err}") from err


@router.get("/{project_id}/vault/secrets", status_code=status.HTTP_200_OK)
async def list_project_secrets(project_id: str) -> Dict[str, Any]:
    """Mengambil daftar nama kunci kredensial tanpa mengekspos nilai plaintext."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    vault = SecretVaultManager()
    try:
        keys = await vault.list_secret_keys(project_id)
        return {
            "status": "success",
            "data": {
                "project_id": project_id,
                "keys": keys,
                "total_stored": len(keys),
            },
        }
    except Exception as err:
        logger.error(f"Gagal membaca daftar kunci vault: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal membaca kunci vault: {err}") from err
