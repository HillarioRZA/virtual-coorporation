"""
Closed-Loop Autonomous Rollback & Self-Healing Engine.
Mendeteksi kegagalan build/test berulang dan secara mandiri memulihkan snapshot GREEN.
"""

from typing import Any, Dict, Optional

from app.core.logger import logger
from app.sandbox.snapshot_manager import snapshot_manager

MAX_CONSECUTIVE_FAILURES = 3


class AutonomousHealer:
    """Manajer pemulihan mandiri sistem saat mendeteksi kegagalan build atau regresi berulang."""

    def __init__(self, failure_threshold: int = MAX_CONSECUTIVE_FAILURES) -> None:
        """Inisialisasi AutonomousHealer."""
        self.threshold = failure_threshold
        self._failure_counters: Dict[str, int] = {}

    def record_success(self, project_id: str) -> None:
        """Mereset counter kegagalan saat kompilasi atau tes berhasil."""
        if project_id in self._failure_counters:
            self._failure_counters[project_id] = 0
            logger.info(f"AutonomousHealer: Counter kegagalan direset untuk [{project_id}]")

    def get_failure_count(self, project_id: str) -> int:
        """Mendapatkan jumlah kegagalan berturut-turut untuk proyek tertentu."""
        return self._failure_counters.get(project_id, 0)

    async def record_failure(
        self,
        project_id: str,
        failure_reason: str = "",
    ) -> Dict[str, Any]:
        """Mencatat kegagalan dan memicu rollback otomatis jika melampaui batas ambang.

        Args:
            project_id: ID proyek sasaran.
            failure_reason: Deskripsi kegagalan kompilasi/tes.

        Returns:
            Dict berisi status pemulihan, apakah rollback terpicu, dan instruksi perbaikan model.
        """
        count = self._failure_counters.get(project_id, 0) + 1
        self._failure_counters[project_id] = count
        logger.warning(f"AutonomousHealer: Kegagalan ke-{count}/{self.threshold} untuk [{project_id}]: {failure_reason}")

        if count < self.threshold:
            return {
                "triggered": False,
                "current_failures": count,
                "threshold": self.threshold,
                "message": f"Kegagalan ke-{count} dicatat. Belum mencapai ambang auto-rollback.",
            }

        # Ambang batas tercapai: cari snapshot GREEN terakhir
        logger.critical(f"AutonomousHealer: Ambang {self.threshold}x kegagalan tercapai pada [{project_id}]. Memicu auto-rollback!")
        snapshots = snapshot_manager.list_snapshots(project_id)
        target_snapshot = next(
            (s for s in snapshots if s.get("tag") in ["GREEN", "PASSED", "STABLE"]),
            None,
        )

        if not target_snapshot and snapshots:
            target_snapshot = snapshots[0]

        if not target_snapshot:
            logger.warning(f"AutonomousHealer: Tidak ada snapshot tersimpan untuk di-rollback pada [{project_id}]")
            return {
                "triggered": False,
                "error": "Tidak ditemukan snapshot stabil untuk dipulihkan.",
            }

        snapshot_id = target_snapshot["id"]
        try:
            rollback_res = await snapshot_manager.rollback_snapshot(project_id, snapshot_id)
            self._failure_counters[project_id] = 0
            from app.core.stream import stream_manager
            await stream_manager.publish(
                project_id=project_id,
                event_type="auto_heal_rollback",
                data={
                    "snapshot_id": snapshot_id,
                    "tag": target_snapshot.get("tag"),
                    "failure_reason": failure_reason,
                    "message": f"Closed-loop auto-rollback berhasil dipulihkan ke {snapshot_id}.",
                },
            )

            directive = (
                "🚨 SIKLUS PERBAIKAN ARSITEKTUR OTONOM DIPICU:\n"
                f"Pendekatan implementasi sebelumnya gagal {self.threshold}x berturut-turut ({failure_reason}).\n"
                f"Sistem telah me-rollback filesystem secara otomatis ke snapshot stabil [{snapshot_id}].\n"
                "Instruksi Model: Rombak total pendekatan arsitektur sebelumnya dan gunakan pola alternatif yang lebih tangguh."
            )

            return {
                "triggered": True,
                "restored_snapshot_id": snapshot_id,
                "tag": target_snapshot.get("tag"),
                "healing_directive": directive,
                "rollback_result": rollback_res,
            }
        except Exception as err:
            logger.error(f"AutonomousHealer: Gagal eksekusi rollback otomatis: {err}")
            return {"triggered": False, "error": str(err)}


autonomous_healer = AutonomousHealer()
