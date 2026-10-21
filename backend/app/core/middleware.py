"""
Custom ASGI Middlewares.
Menyediakan gerbang autentikasi personal SecurityGateMiddleware dan pencatatan metrik performa ProcessTimeLoggingMiddleware.
"""

import time
from typing import Any, Dict
from fastapi import status
from fastapi.responses import JSONResponse

from app.core.auth_manager import auth_manager
from app.core.logger import logger


class SecurityGateMiddleware:
    """Gembok keamanan personal murni ASGI: memvalidasi session token tanpa overhead BaseHTTPMiddleware."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "")
        if method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        public_prefixes = (
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/auth/status",
            "/api/v1/auth/verify",
            "/api/v1/corporate/office",
            "/api/v1/corporate/roles",
            "/api/v1/sentinel",
            "/api/v1/mcp/all-tools",
            "/api/v1/mcp/servers",
            "/api/v1/skills",
        )
        if any(path == p or path.startswith(p + "/") for p in public_prefixes):
            await self.app(scope, receive, send)
            return

        if auth_manager.is_enabled() and path.startswith("/api/v1"):
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode("latin1")
            token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else None
            if not token and b"token=" in scope.get("query_string", b""):
                qs_parts = dict(kv.split(b"=", 1) for kv in scope.get("query_string", b"").split(b"&") if b"=" in kv)
                token = qs_parts.get(b"token", b"").decode("latin1")

            if not auth_manager.verify_session_token(token):
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"status": "error", "message": "Akses ditolak. Sesi tidak valid atau telah kedaluwarsa."},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


class ProcessTimeLoggingMiddleware:
    """Middleware murni ASGI untuk mencatat durasi request dan header X-Process-Time."""

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()

        async def send_wrapper(message: Dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                process_time = time.perf_counter() - start_time
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", f"{process_time:.4f}s".encode("latin1")))
                message["headers"] = headers
                logger.debug(
                    f"HTTP {scope.get('method')} {scope.get('path')} - {message.get('status')} [{process_time:.4f}s]"
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)
