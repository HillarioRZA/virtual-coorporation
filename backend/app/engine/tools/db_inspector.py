"""
Database Introspection & Read-Only Query Tool.
Menyediakan inspeksi skema tabel dan query baca-saja yang aman untuk agen backend.
"""

from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, List, Optional

from app.core.logger import logger

MUTATION_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|ATTACH|DETACH|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


class DatabaseInspector:
    """Inspektor skema database SQLite mandiri dengan penegakan izin baca-saja mutlak."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi DatabaseInspector."""
        self.projects_dir = projects_dir or Path("projects_output")

    def _resolve_db_path(self, project_id: str, relative_db_path: str = "backend/venture.db") -> Path:
        """Mendapatkan path absolut berkas database proyek."""
        db_path = self.projects_dir / project_id / relative_db_path
        if not db_path.exists():
            # Coba cari berkas .db apa pun di direktori backend proyek
            be_dir = self.projects_dir / project_id / "backend"
            if be_dir.exists():
                found = list(be_dir.glob("*.db"))
                if found:
                    return found[0]
        return db_path

    def list_tables(self, project_id: str, db_name: str = "venture.db") -> List[str]:
        """Mendapatkan daftar seluruh tabel aktif di database proyek."""
        db_path = self._resolve_db_path(project_id, f"backend/{db_name}")
        if not db_path.exists():
            logger.warning(f"Database tidak ditemukan untuk inspeksi: {db_path}")
            return []

        try:
            uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as err:
            logger.error(f"Gagal introspeksi daftar tabel [{project_id}]: {err}")
            return []

    def inspect_table_schema(self, project_id: str, table_name: str, db_name: str = "venture.db") -> Dict[str, Any]:
        """Mengambil informasi kolom, tipe data, primary key, dan foreign key tabel."""
        db_path = self._resolve_db_path(project_id, f"backend/{db_name}")
        if not db_path.exists():
            return {"error": f"Database {db_name} tidak ditemukan", "table": table_name}

        try:
            uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info('{table_name}');")
                columns = [
                    {"cid": r[0], "name": r[1], "type": r[2], "notnull": bool(r[3]), "dflt_value": r[4], "pk": bool(r[5])}
                    for r in cursor.fetchall()
                ]
                cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
                foreign_keys = [
                    {"id": r[0], "seq": r[1], "table": r[2], "from": r[3], "to": r[4]}
                    for r in cursor.fetchall()
                ]
                return {"table": table_name, "columns": columns, "foreign_keys": foreign_keys}
        except sqlite3.Error as err:
            logger.error(f"Gagal introspeksi skema tabel [{table_name}]: {err}")
            return {"error": str(err), "table": table_name}

    def execute_safe_query(
        self, project_id: str, query: str, limit: int = 5, db_name: str = "venture.db"
    ) -> Dict[str, Any]:
        """Mengeksekusi query SELECT baca-saja dan mengembalikan contoh baris riil."""
        stripped = query.strip()
        if MUTATION_PATTERN.search(stripped):
            logger.warning(f"Query ditolak karena mengandung mutasi: {stripped}")
            return {"error": "Hanya operasi SELECT dan PRAGMA baca-saja yang diizinkan."}

        db_path = self._resolve_db_path(project_id, f"backend/{db_name}")
        if not db_path.exists():
            return {"error": f"Database {db_name} tidak ditemukan"}

        safe_limit = max(1, min(limit, 20))
        if not re.search(r"\bLIMIT\b", stripped, re.IGNORECASE):
            stripped = f"{stripped.rstrip(';')} LIMIT {safe_limit};"

        try:
            uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=5.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(stripped)
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description] if cursor.description else []
                data = [dict(r) for r in rows]
                return {"query": stripped, "columns": cols, "rows": data, "count": len(data)}
        except sqlite3.Error as err:
            logger.error(f"Gagal eksekusi query baca-saja [{stripped}]: {err}")
            return {"error": str(err), "query": stripped}


db_inspector = DatabaseInspector()
