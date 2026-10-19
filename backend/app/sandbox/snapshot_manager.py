"""
Copy-on-Write (CoW) Filesystem Snapshot & Rollback Engine.
Menyediakan pembekuan state file direktori proyek dan pemulihan 1-klik yang aman.
"""

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
import uuid

from app.core.logger import logger
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus

IGNORED_DIRS = {".snapshots", "__pycache__", "node_modules", ".git", ".pytest_cache"}
IGNORED_FILES = {".DS_Store", "Thumbs.db"}


class SnapshotManager:
    """Pengelola snapshot instan dan pemulihan direktori proyek."""

    def __init__(self, base_output_dir: Optional[Path] = None) -> None:
        """Inisialisasi SnapshotManager."""
        self.base_output_dir = base_output_dir or Path("projects_output")

    def _get_project_dir(self, project_id: str) -> Path:
        """Mendapatkan path direktori proyek sasaran."""
        p_dir = self.base_output_dir / project_id
        p_dir.mkdir(parents=True, exist_ok=True)
        return p_dir

    def _get_snapshots_dir(self, project_id: str) -> Path:
        """Mendapatkan path direktori .snapshots proyek."""
        s_dir = self._get_project_dir(project_id) / ".snapshots"
        s_dir.mkdir(parents=True, exist_ok=True)
        return s_dir

    def _load_manifest(self, project_id: str) -> List[Dict[str, Any]]:
        """Memuat daftar riwayat snapshot dari manifest.json."""
        manifest_file = self._get_snapshots_dir(project_id) / "manifest.json"
        if not manifest_file.exists():
            return []
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            logger.warning(f"Gagal membaca manifest snapshot [{project_id}]: {err}")
            return []

    def _save_manifest(self, project_id: str, manifest: List[Dict[str, Any]]) -> None:
        """Menyimpan daftar riwayat snapshot ke manifest.json."""
        manifest_file = self._get_snapshots_dir(project_id) / "manifest.json"
        try:
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
        except Exception as err:
            logger.error(f"Gagal menyimpan manifest snapshot [{project_id}]: {err}")

    def create_snapshot(
        self,
        project_id: str,
        tag: str = "MANUAL",
        description: str = "",
    ) -> Dict[str, Any]:
        """Membekukan direktori proyek ke snapshot baru."""
        project_dir = self._get_project_dir(project_id)
        snapshot_id = f"snap_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        target_snap_dir = self._get_snapshots_dir(project_id) / snapshot_id
        target_snap_dir.mkdir(parents=True, exist_ok=True)

        file_count, total_bytes = 0, 0
        for item in project_dir.iterdir():
            if item.name in IGNORED_DIRS or item.name in IGNORED_FILES:
                continue
            dest = target_snap_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(*IGNORED_DIRS, *IGNORED_FILES), dirs_exist_ok=True)
                for f in dest.rglob("*"):
                    if f.is_file():
                        file_count += 1
                        total_bytes += f.stat().st_size
            else:
                shutil.copy2(item, dest)
                file_count += 1
                total_bytes += item.stat().st_size

        snapshot_meta = {
            "id": snapshot_id,
            "project_id": project_id,
            "tag": tag.upper(),
            "description": description or f"Snapshot {tag}",
            "file_count": file_count,
            "total_bytes": total_bytes,
            "created_at": datetime.utcnow().isoformat(),
        }

        manifest = self._load_manifest(project_id)
        manifest.insert(0, snapshot_meta)
        self._save_manifest(project_id, manifest)
        logger.info(f"Snapshot [{snapshot_id}] dibuat untuk [{project_id}] ({file_count} files, {total_bytes} bytes)")
        return snapshot_meta

    def list_snapshots(self, project_id: str) -> List[Dict[str, Any]]:
        """Mendapatkan seluruh riwayat snapshot untuk proyek tertentu."""
        return self._load_manifest(project_id)

    async def rollback_snapshot(self, project_id: str, snapshot_id: str) -> Dict[str, Any]:
        """Memulihkan berkas proyek ke kondisi snapshot sasaran dengan safety backup otomatis."""
        snapshots = self.list_snapshots(project_id)
        target_meta = next((s for s in snapshots if s["id"] == snapshot_id), None)
        if not target_meta:
            raise FileNotFoundError(f"Snapshot [{snapshot_id}] tidak ditemukan untuk proyek [{project_id}]")

        source_dir = self._get_snapshots_dir(project_id) / snapshot_id
        if not source_dir.exists():
            raise FileNotFoundError(f"Direktori data snapshot [{source_dir}] tidak ditemukan")

        # Safety checkpoint otomatis sebelum rollback
        self.create_snapshot(project_id, tag="AUTO_PRE_ROLLBACK", description=f"Safety backup sebelum rollback ke {snapshot_id}")
        project_dir = self._get_project_dir(project_id)

        # Hapus berkas aktif kecuali .snapshots
        for item in project_dir.iterdir():
            if item.name == ".snapshots":
                continue
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                try:
                    item.unlink(missing_ok=True)
                except Exception:
                    pass

        # Salin kembali dari snapshot
        for item in source_dir.iterdir():
            dest = project_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

        logger.info(f"Rollback berhasil: proyek [{project_id}] dipulihkan ke [{snapshot_id}]")
        try:
            msg = CorporateMessageCreate(
                project_id=project_id,
                sender_role_id="role_cto",
                event_type="SNAPSHOT_ROLLBACK",
                content=f"Filesystem dipulihkan ke snapshot [{snapshot_id}] ({target_meta.get('tag')}: {target_meta.get('description')}).",
            )
            await corporate_event_bus.publish(msg)
        except Exception as err:
            logger.warning(f"Gagal broadcast rollback event ke bus: {err}")

        return {
            "status": "success",
            "project_id": project_id,
            "restored_snapshot_id": snapshot_id,
            "tag": target_meta.get("tag"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def delete_snapshot(self, project_id: str, snapshot_id: str) -> bool:
        """Menghapus snapshot dari direktori dan manifest."""
        manifest = self._load_manifest(project_id)
        new_manifest = [s for s in manifest if s["id"] != snapshot_id]
        if len(new_manifest) == len(manifest):
            return False

        target_dir = self._get_snapshots_dir(project_id) / snapshot_id
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        self._save_manifest(project_id, new_manifest)
        logger.info(f"Snapshot [{snapshot_id}] dihapus dari proyek [{project_id}]")
        return True


snapshot_manager = SnapshotManager()
