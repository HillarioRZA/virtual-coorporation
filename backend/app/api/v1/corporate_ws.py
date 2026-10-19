"""
Corporate Live Lounge WebSocket Streaming Endpoint.
Mengalirkan pertukaran pesan inter-agent dan menerima instruksi langsung Chairman secara real-time.
"""

import asyncio
import json
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus

router = APIRouter(prefix="/corporate/ws", tags=["Corporate WebSocket Lounge"])


@router.websocket("/lounge/{project_id}")
async def websocket_lounge_stream(websocket: WebSocket, project_id: str) -> None:
    """Mengalirkan pesan Lounge inter-agent secara real-time dan menerima input Chairman."""
    await websocket.accept()
    logger.info(f"WebSocket Lounge Connected: Project [{project_id}]")

    # 1. Kirim riwayat pesan terdahulu dalam urutan kronologis
    try:
        history = await corporate_event_bus.get_history(project_id, limit=30)
        # Balikkan urutan agar pesan tertua muncul duluan di chat
        chronological_history = list(reversed(history))
        await websocket.send_json({
            "type": "HISTORY",
            "messages": chronological_history,
        })
    except Exception as err:
        logger.warning(f"Gagal memuat riwayat awal Lounge: {err}")

    # 2. Berlangganan ke Event Bus proyek
    event_queue = await corporate_event_bus.subscribe(project_id)

    async def _send_events() -> None:
        """Mengirimkan event bus baru ke koneksi WebSocket client."""
        while True:
            event_payload = await event_queue.get()
            try:
                await websocket.send_json({
                    "type": "MESSAGE",
                    "data": event_payload,
                })
            except Exception:
                break

    send_task = asyncio.create_task(_send_events())

    # 3. Dengarkan pesan instruksi masuk dari Chairman / Client
    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                parsed = json.loads(text_data)
                content = parsed.get("content", "").strip()
                sender = parsed.get("sender_role_id", "CHAIRMAN")
            except Exception:
                content = text_data.strip()
                sender = "CHAIRMAN"

            if content:
                # Siarkan ke Corporate Event Bus
                await corporate_event_bus.publish(
                    CorporateMessageCreate(
                        branch_id="branch_main",
                        project_id=project_id,
                        channel_type="LOUNGE",
                        sender_role_id=sender,
                        event_type="MESSAGE",
                        content=content,
                    )
                )
    except WebSocketDisconnect:
        logger.info(f"WebSocket Lounge Disconnected: Project [{project_id}]")
    except Exception as err:
        logger.error(f"WebSocket Lounge Error: {err}")
    finally:
        send_task.cancel()
        await corporate_event_bus.unsubscribe(project_id, event_queue)
