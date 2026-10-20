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
        await dynamic_settings_manager.load_overrides()
        from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry
        await dynamic_tool_registry.load_approved_tools_from_db()

        from app.engine.mcp.mcp_manager import mcp_manager
        await mcp_manager.rehydrate_active_servers()

        # Pre-warm model FastEmbed neural embedding secara asinkron di worker thread
        try:
            from app.engine.memory.vector_store import vector_store
            await asyncio.to_thread(vector_store.embed_text, "prewarming neural model")
            logger.info("Lifespan: Model FastEmbed ONNX berhasil di-prewarm.")
        except Exception as v_err:
            logger.debug(f"Lifespan: FastEmbed prewarming dilewati: {v_err}")

        # Jalankan Telegram Secretary Daemon jika bot token tersedia
        from app.engine.secretary.telegram_daemon import telegram_secretary
        if getattr(settings, "TELEGRAM_BOT_TOKEN", None):
            telegram_secretary.start()
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

    try:
        from app.engine.secretary.telegram_daemon import telegram_secretary
        telegram_secretary.stop()
        from app.engine.runtime.kanban_runner import kanban_runner
        kanban_runner.stop_background_runner()
    except Exception as cleanup_err:
        logger.debug(f"Cleanup error saat shutdown: {cleanup_err}")

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



from app.core.middleware import ProcessTimeLoggingMiddleware, SecurityGateMiddleware

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
