"""
WebSocket Endpoint untuk Interactive Sandbox Terminal.
Streaming dua arah real-time antara antarmuka web dan subproses terminal di direktori proyek.
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.sandbox.terminal_manager import terminal_manager

router = APIRouter(tags=["Sandbox Terminal WS"])


@router.websocket("/sandbox/ws/terminal/{project_id}")
async def sandbox_terminal_websocket(websocket: WebSocket, project_id: str) -> None:
    """WebSocket endpoint untuk sesi terminal shell interaktif pada direktori proyek.

    Args:
        websocket: Koneksi WebSocket aktif.
        project_id: ID proyek sasaran.
    """
    await websocket.accept()
    cwd_path = terminal_manager.get_working_directory(project_id)
    logger.info(f"Terminal WS terhubung untuk proyek [{project_id}] di [{cwd_path}]")

    try:
        # Kirim banner pembuka sistem
        welcome_banner = {
            "type": "system",
            "data": (
                "⚡ UNIVERSAL SANDBOX TERMINAL (v2.0)\n"
                f"📁 Working Directory: {cwd_path}\n"
                "💡 Status: Siap menerima perintah shell. Gunakan tombol preset atau ketik manual.\n\n"
            ),
        }
        await websocket.send_json(welcome_banner)
        while True:
            raw_data = await websocket.receive_text()
            cmd = ""
            try:
                msg_json = json.loads(raw_data)
                cmd = msg_json.get("command", "")
            except Exception:
                cmd = raw_data.strip()

            if not cmd:
                continue

            logger.info(f"Menerima perintah terminal dari UI: [{cmd}] untuk [{project_id}]")

            # Eksekusi dan streaming output chunk-by-chunk
            async for event in terminal_manager.execute_command_stream(project_id, cmd):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info(f"Terminal WS terputus untuk proyek [{project_id}]")
    except Exception as err:
        logger.warning(f"Error pada sesi Terminal WS [{project_id}]: {err}")
        try:
            await websocket.send_json({"type": "stderr", "data": f"Session Error: {err}\n"})
        except Exception:
            pass
