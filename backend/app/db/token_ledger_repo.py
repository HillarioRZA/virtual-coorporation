"""Corporate Token Ledger Repository.

Mengelola pencatatan transaksi konsumsi token, perhitungan biaya kredit,
dan pemantauan status kesehatan kanal upstream model router.
"""

from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class TokenLedgerRepository:
    """Repositori asinkron untuk pencatatan token ledger dan analitik biaya CFO."""

    async def record_token_usage(
        self,
        project_id: Optional[str],
        branch_id: Optional[str],
        pipeline_id: Optional[str],
        role_id: Optional[str],
        model_name: str,
        provider: str,
        upstream_channel: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int = 0,
        cost_usd: float = 0.0,
        status: str = "SUCCESS",
        is_fallback: bool = False,
        error_message: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mencatat transaksi penggunaan token ke dalam corporate_token_ledger."""
        record_id = f"tx_{uuid.uuid4().hex[:12]}"
        total_tokens = input_tokens + output_tokens

        query = """
        INSERT INTO corporate_token_ledger
        (id, project_id, branch_id, pipeline_id, role_id, model_name, provider,
         upstream_channel, input_tokens, output_tokens, total_tokens, latency_ms,
         cost_usd, status, is_fallback, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            record_id, project_id, branch_id, pipeline_id, role_id, model_name,
            provider, upstream_channel, input_tokens, output_tokens, total_tokens,
            latency_ms, cost_usd, status, 1 if is_fallback else 0, error_message
        )
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute(query, params)
                await conn.commit()
                return {
                    "id": record_id,
                    "total_tokens": total_tokens,
                    "cost_usd": cost_usd,
                    "status": status,
                    "is_fallback": is_fallback,
                }
        except aiosqlite.Error as err:
            logger.error(f"Gagal mencatat token ledger: {err}")
            raise

    async def get_token_summary(
        self,
        project_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mengambil ringkasan total token, total biaya, dan rasio fallback."""
        conditions: List[str] = []
        params: List[Any] = []
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if branch_id:
            conditions.append("branch_id = ?")
            params.append(branch_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
        SELECT 
            COALESCE(SUM(input_tokens), 0) as total_input,
            COALESCE(SUM(output_tokens), 0) as total_output,
            COALESCE(SUM(total_tokens), 0) as grand_tokens,
            COALESCE(SUM(cost_usd), 0.0) as grand_cost,
            COUNT(*) as total_requests,
            COALESCE(SUM(CASE WHEN is_fallback = 1 THEN 1 ELSE 0 END), 0) as total_fallbacks
        FROM corporate_token_ledger {where_clause};
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, params) as cur:
                row = await cur.fetchone()
                return {
                    "total_input_tokens": int(row["total_input"] if row else 0),
                    "total_output_tokens": int(row["total_output"] if row else 0),
                    "total_tokens": int(row["grand_tokens"] if row else 0),
                    "total_cost_usd": round(float(row["grand_cost"] if row else 0.0), 4),
                    "total_requests": int(row["total_requests"] if row else 0),
                    "total_fallbacks": int(row["total_fallbacks"] if row else 0),
                }

    async def get_role_burn_rates(
        self,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil pengeluaran token dan biaya per peran karyawan AI."""
        query = """
        SELECT 
            COALESCE(role_id, 'unassigned') as role,
            model_name,
            provider,
            COALESCE(SUM(total_tokens), 0) as tokens,
            COALESCE(SUM(cost_usd), 0.0) as cost_usd,
            COUNT(*) as request_count,
            COALESCE(SUM(CASE WHEN is_fallback = 1 THEN 1 ELSE 0 END), 0) as fallback_count
        FROM corporate_token_ledger
        GROUP BY role_id, model_name, provider
        ORDER BY tokens DESC;
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query) as cur:
                rows = await cur.fetchall()
                return [
                    {
                        "role_id": r["role"],
                        "role_name": r["role"],
                        "model_name": r["model_name"],
                        "provider": r["provider"],
                        "total_tokens": int(r["tokens"]),
                        "cost_usd": round(float(r["cost_usd"]), 4),
                        "total_cost_usd": round(float(r["cost_usd"]), 4),
                        "request_count": int(r["request_count"]),
                        "fallback_count": int(r["fallback_count"]),
                        "fallbacks_count": int(r["fallback_count"]),
                    }
                    for r in rows
                ]

    async def get_burn_rate_timeline(
        self,
        days: int = 7,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil rekap konsumsi token harian untuk visualisasi grafik CFO."""
        query = """
        SELECT 
            DATE(timestamp) as date_label,
            COALESCE(SUM(total_tokens), 0) as daily_tokens,
            COALESCE(SUM(cost_usd), 0.0) as daily_cost,
            COUNT(*) as request_count
        FROM corporate_token_ledger
        GROUP BY DATE(timestamp)
        ORDER BY date_label ASC
        LIMIT ?;
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, (days,)) as cur:
                rows = await cur.fetchall()
                return [
                    {
                        "date": str(r["date_label"]),
                        "tokens": int(r["daily_tokens"]),
                        "cost_usd": round(float(r["daily_cost"]), 4),
                        "requests": int(r["request_count"]),
                    }
                    for r in rows
                ]


token_ledger_repo = TokenLedgerRepository()
