"""
Repository Akses Data Sentinel Audit Trail.
Menyimpan dan mengkueri catatan inspeksi CoV, metrik reliabilitas, dan diff log.
"""

import json
from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class SentinelAuditRepo:
    """Manajer persistensi log audit CoV Sentinel pada basis data SQLite."""

    async def record_audit(
        self, project_id: str, agent_role: str, status: str, original_content: str,
        inspected_content: str, tool_name: Optional[str] = None,
        tool_parameters: Optional[Dict[str, Any]] = None, repair_feedback: Optional[str] = None,
        repairs_count: int = 0, latency_ms: float = 0.0, custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menyimpan entri audit CoV baru ke basis data."""
        audit_id = f"sentinel_{uuid.uuid4().hex[:12]}"
        params_str = json.dumps(tool_parameters) if tool_parameters is not None else None
        sql = (
            "INSERT INTO sentinel_audit_logs (id, project_id, agent_role, status, tool_name, "
            "tool_parameters, original_content, inspected_content, repair_feedback, repairs_count, latency_ms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute(
                    sql,
                    (audit_id, project_id, agent_role, status, tool_name, params_str,
                     original_content, inspected_content, repair_feedback, repairs_count, round(latency_ms, 2)),
                )
                await conn.commit()
            return {
                "id": audit_id, "project_id": project_id, "agent_role": agent_role, "status": status,
                "tool_name": tool_name, "tool_parameters": tool_parameters, "original_content": original_content,
                "inspected_content": inspected_content, "repair_feedback": repair_feedback,
                "repairs_count": repairs_count, "latency_ms": round(latency_ms, 2),
            }
        except (aiosqlite.Error, OSError) as err:
            logger.error(f"Gagal mencatat audit log Sentinel: {err}")
            return {"id": audit_id, "error": str(err)}

    async def get_audit_logs(
        self, project_id: str, limit: int = 50, role: Optional[str] = None,
        status: Optional[str] = None, custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil riwayat log audit Sentinel untuk proyek tertentu."""
        clauses = ["project_id = ?"]
        params: List[Any] = [project_id]
        if role:
            clauses.append("agent_role = ?")
            params.append(role.upper())
        if status:
            clauses.append("status = ?")
            params.append(status.upper())

        sql = (
            f"SELECT id, project_id, agent_role, status, tool_name, tool_parameters, "
            f"original_content, inspected_content, repair_feedback, repairs_count, latency_ms, created_at "
            f"FROM sentinel_audit_logs WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT ?"
        )
        params.append(limit)
        results: List[Dict[str, Any]] = []
        try:
            async with get_db_connection(custom_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(sql, tuple(params)) as cursor:
                    rows = await cursor.fetchall()
                    for r in rows:
                        item = dict(r)
                        if item.get("tool_parameters"):
                            try:
                                item["tool_parameters"] = json.loads(item["tool_parameters"])
                            except json.JSONDecodeError:
                                pass
                        results.append(item)
            return results
        except (aiosqlite.Error, OSError) as err:
            logger.error(f"Gagal membaca audit logs Sentinel: {err}")
            return []

    async def get_audit_stats(self, project_id: str, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Mengagregasi statistik performa dan reliabilitas inspeksi CoV."""
        sql = """
        SELECT COUNT(*) as total,
            SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'REPAIRED' THEN 1 ELSE 0 END) as repaired,
            SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
            AVG(latency_ms) as avg_latency
        FROM sentinel_audit_logs WHERE project_id = ?
        """
        try:
            async with get_db_connection(custom_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(sql, (project_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row or row["total"] == 0:
                        return self._empty_stats()
                    tot, app, rep, rej = row["total"], row["approved"] or 0, row["repaired"] or 0, row["rejected"] or 0
                    return {
                        "total_inspections": tot, "approved_count": app, "repaired_count": rep,
                        "rejected_count": rej, "reliability_rate": round(((app + rep) / tot) * 100.0, 1),
                        "avg_latency_ms": round(row["avg_latency"] or 0.0, 1),
                    }
        except (aiosqlite.Error, OSError) as err:
            logger.error(f"Gagal menghitung statistik audit Sentinel: {err}")
            return self._empty_stats()

    get_project_stats = get_audit_stats

    def _empty_stats(self) -> Dict[str, Any]:
        """Kembalian default saat statistik kosong."""
        return {
            "total_inspections": 0, "approved_count": 0, "repaired_count": 0,
            "rejected_count": 0, "reliability_rate": 100.0, "avg_latency_ms": 0.0,
        }


sentinel_repo = SentinelAuditRepo()
