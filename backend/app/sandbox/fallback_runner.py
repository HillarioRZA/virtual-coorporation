"""
Ephemeral Fallback HTTP & Mock Multi-Service Server.
Menyediakan server prototipe lokal mandiri berbasis asyncio saat Docker Engine offline.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.logger import logger


class FallbackRunner:
    """Manajer server HTTP fallback asinkron lokal tanpa ketergantungan Docker daemon."""

    def __init__(self) -> None:
        """Inisialisasi registry server fallback aktif."""
        self.fallback_servers: Dict[str, asyncio.Server] = {}

    def _generate_interactive_html(self, project_id: str, host_code_path: str, port: int) -> str:
        """Menghasilkan halaman HTML pratinjau interaktif dari berkas Next.js yang dihasilkan."""
        code_dir = Path(host_code_path)
        page_file = code_dir / "src" / "app" / "page.tsx"
        feature_file = code_dir / "src" / "components" / "CoreFeature.tsx"

        page_snippet = page_file.read_text(encoding="utf-8") if page_file.exists() else "// page.tsx"
        feature_snippet = feature_file.read_text(encoding="utf-8") if feature_file.exists() else "// CoreFeature.tsx"

        return f"""<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Live Preview Sandbox - {project_id}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>.bg-fluid {{ background: radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 40%), #070709; }}</style>
</head>
<body class="bg-fluid min-h-screen text-slate-100 p-6 flex flex-col justify-between font-sans">
  <header class="max-w-4xl mx-auto w-full mb-6 p-4 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white text-xs">⚡</div>
      <div>
        <h1 class="text-sm font-bold text-white flex items-center gap-2">Live Interactive Sandbox (Multi-Service Fallback)</h1>
        <p class="text-xs text-slate-400 font-mono">Port: {port} • Project: {project_id}</p>
      </div>
    </div>
    <span class="text-xs px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-mono">STATUS 200 OK</span>
  </header>
  <main class="max-w-4xl mx-auto w-full flex-1 p-6 rounded-3xl bg-slate-900/60 border border-white/10 space-y-4">
    <div class="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/30 text-xs text-indigo-300">
      Simulated Full-Stack Active: Frontend (:3000) • Mock API (:8000) • In-Memory DB (:5432)
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="p-4 rounded-xl bg-black/40 border border-slate-800 text-xs font-mono">
        <div class="text-indigo-400 pb-1 border-b border-slate-800">src/app/page.tsx</div>
        <pre class="text-slate-300 text-[11px] overflow-x-auto max-h-40 pt-2">{page_snippet[:350]}</pre>
      </div>
      <div class="p-4 rounded-xl bg-black/40 border border-slate-800 text-xs font-mono">
        <div class="text-cyan-400 pb-1 border-b border-slate-800">src/components/CoreFeature.tsx</div>
        <pre class="text-slate-300 text-[11px] overflow-x-auto max-h-40 pt-2">{feature_snippet[:350]}</pre>
      </div>
    </div>
  </main>
  <footer class="max-w-4xl mx-auto w-full mt-6 text-center text-xs text-slate-500">Universal Ephemeral Sandbox • Virtual Tech Startup</footer>
</body></html>"""

    async def start_fallback_http_server(self, project_id: str, host_code_path: str, port: int) -> None:
        """Memulai HTTP server berbasis asyncio lokal saat Docker tidak tersedia."""
        html_bytes = self._generate_interactive_html(project_id, host_code_path, port).encode("utf-8")

        async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            try:
                line = await reader.readline()
                while True:
                    hdr = await reader.readline()
                    if not hdr or hdr in (b"\r\n", b"\n"):
                        break
                resp = (
                    b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n"
                    b"Content-Length: " + str(len(html_bytes)).encode() + b"\r\n"
                    b"Connection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\n" + html_bytes
                )
                writer.write(resp)
                await writer.drain()
            except Exception:
                pass
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        server = await asyncio.start_server(handle_client, "127.0.0.1", port)
        self.fallback_servers[project_id] = server
        logger.info(f"Fallback async server aktif pada http://127.0.0.1:{port} [{project_id}]")

    async def stop_fallback_server(self, project_id: str) -> bool:
        """Menghentikan server fallback proyek."""
        server = self.fallback_servers.pop(project_id, None)
        if server:
            try:
                server.close()
                await server.wait_closed()
                logger.info(f"Fallback server untuk [{project_id}] berhasil dihentikan.")
            except Exception as err:
                logger.warning(f"Error saat menghentikan fallback server: {err}")
        return True

    def get_fallback_metrics(self, project_id: str) -> Dict[str, Any]:
        """Menghasilkan metrik sumber daya simulated untuk lingkungan fallback."""
        is_active = project_id in self.fallback_servers
        return {
            "project_id": project_id,
            "mode": "fallback",
            "cpu_limit_cores": 1.5,
            "cpu_used_cores": 0.18 if is_active else 0.0,
            "cpu_percent": 12.0 if is_active else 0.0,
            "memory_limit_mb": 1024,
            "memory_used_mb": 45.5 if is_active else 0.0,
            "memory_percent": 4.4 if is_active else 0.0,
            "services": [
                {"name": "frontend", "status": "RUNNING" if is_active else "STOPPED", "port": 3000},
                {"name": "backend", "status": "SIMULATED" if is_active else "STOPPED", "port": 8000},
                {"name": "database", "status": "IN_MEMORY" if is_active else "STOPPED", "port": 5432},
            ],
        }


fallback_runner = FallbackRunner()
