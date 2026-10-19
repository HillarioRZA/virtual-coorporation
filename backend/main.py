"""
Main FastAPI Application Entrypoint.
Mengintegrasikan CORS, middleware logging, inisialisasi basis data, dan router API v1.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import sys
import time
from typing import Any, AsyncGenerator, Dict

# Daftarkan direktori backend ke sys.path agar modul 'app' dapat ditemukan secara universal
BACKEND_DIR = str(Path(__file__).resolve().parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.logger import logger
import asyncio
from app.core.auth_manager import auth_manager
from app.core.settings_manager import dynamic_settings_manager
from app.db.init_db import init_database


async def _auth_rotation_worker() -> None:
    """Worker background untuk memeriksa kedaluwarsa password dan melakukan rotasi."""
    while True:
        try:
            await auth_manager.check_and_rotate_if_needed()
        except asyncio.CancelledError:
            break
        except Exception as err:
            logger.warning(f"Kesalahan pada worker rotasi autentikasi: {err}")
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler untuk inisialisasi dan cleanup sumber daya."""
    logger.info("Memulai aplikasi FastAPI & menginisialisasi basis data SQLite...")
    try:
        await init_database()
        logger.info("Basis data SQLite berhasil diinisialisasi.")
        await dynamic_settings_manager.load_overrides()
    except Exception as err:
        logger.error(f"Gagal menginisialisasi basis data saat startup: {err}")
        raise

    # Jalankan worker background rotasi password
    worker_task = asyncio.create_task(_auth_rotation_worker())

    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("Aplikasi FastAPI sedang dimatikan (graceful shutdown)...")


app = FastAPI(
    title="Virtual Tech Startup Multi-Agent System API",
    description="Native Python Orchestration Engine & Universal Venture Incubator Hub",
    version="1.0.0",
    lifespan=lifespan,
)

# Konfigurasi Cross-Origin Resource Sharing (CORS)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    f"http://localhost:{settings.FRONTEND_PORT}",
    f"http://127.0.0.1:{settings.FRONTEND_PORT}",
    "*",
]



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
            "/api/v1/sentinel",
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


app.add_middleware(ProcessTimeLoggingMiddleware)
app.add_middleware(SecurityGateMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Penanganan error validasi skema input Pydantic."""
    logger.warning(f"Validation error pada {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "Validasi skema payload gagal.", "details": exc.errors()},
    )


@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Endpoint pemantauan kesehatan layanan backend."""
    return {
        "status": "healthy",
        "service": "venture-incubator-hub",
        "version": "1.0.0",
        "env": settings.APP_ENV,
    }


# Mount seluruh router API v1
app.include_router(api_v1_router, prefix="/api/v1")
