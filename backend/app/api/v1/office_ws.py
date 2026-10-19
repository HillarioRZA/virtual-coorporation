"""
WebSocket Streaming Router untuk Virtual World Corporate Office Simulator.
Mengalirkan snapshot koordinat spasial, mutasi event, dan menerima interaksi real-time dari browser.
"""

import asyncio
import json
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.office.office_simulator import office_sim_engine

router = APIRouter(tags=["Office Simulator WebSocket"])


@router.websocket("/corporate/ws/office/{project_id}")
async def office_simulation_websocket(websocket: WebSocket, project_id: str) -> None:
    """Mengalirkan state koordinat dan status aktivitas agen AI secara real-time ke kanvas Next.js."""
    await websocket.accept()
    logger.info(f"WebSocket Office terhubung untuk venture [{project_id}]")

    # 1. Kirim snapshot awal tata letak dan agen
    init_snap = office_sim_engine.get_snapshot()
    await websocket.send_json({"type": "INIT_STATE", "data": init_snap})

    queue = await corporate_event_bus.subscribe(project_id)

    async def event_forwarder() -> None:
        """Meneruskan mutasi event dari EventBus ke WebSocket client."""
        try:
            while True:
                evt = await queue.get()
                evt_type = evt.get("event_type", "MESSAGE") if isinstance(evt, dict) else getattr(evt, "event_type", "MESSAGE")
                payload = evt if isinstance(evt, dict) else getattr(evt, "payload", {})
                office_sim_engine.handle_bus_event(evt_type, payload)
                snap = office_sim_engine.get_snapshot()

                content = getattr(evt, "content", "") if not isinstance(evt, dict) else evt.get("content", "")
                sender_id = getattr(evt, "sender_role_id", "role_system") if not isinstance(evt, dict) else evt.get("sender_role_id", "role_system")
                recipient_id = getattr(evt, "recipient_role_id", None) if not isinstance(evt, dict) else evt.get("recipient_role_id")
                ticket_id = getattr(evt, "ticket_id", None) if not isinstance(evt, dict) else evt.get("ticket_id")

                stream_msg = None
                if content:
                    stream_msg = {
                        "id": f"evt_{project_id}_{int(asyncio.get_event_loop().time() * 1000)}",
                        "projectId": project_id,
                        "senderRoleId": sender_id,
                        "recipientRoleId": recipient_id,
                        "ticketId": ticket_id,
                        "eventType": evt_type,
                        "content": content,
                        "category": "LOUNGE" if evt_type in ("DIRECTIVE_INTERRUPTION", "DIRECTIVE_RESPONSE", "AGENT_THINKING") else "EXECUTION",
                    }

                await websocket.send_json({
                    "type": "OFFICE_UPDATE",
                    "event": evt_type,
                    "agents": snap["agents"],
                    "stream_event": stream_msg,
                })
        except asyncio.CancelledError:
            pass

    async def client_listener() -> None:
        """Menerima arahan atau event pemicu dari interaksi pengguna di kanvas browser."""
        try:
            while True:
                msg_text = await websocket.receive_text()
                msg: Dict[str, Any] = json.loads(msg_text)
                mtype = msg.get("type")

                if mtype == "CALL_MEETING":
                    office_sim_engine.handle_bus_event("CALL_MEETING", {})
                elif mtype == "INTERVENE":
                    office_sim_engine.intervene_agent(
                        role_id=msg.get("role_id", ""),
                        instruction=msg.get("instruction", ""),
                    )
                elif mtype == "DEMO_STEP":
                    office_sim_engine.step_simulation()

                # Balas snapshot terkini setelah mutasi interaksi
                snap = office_sim_engine.get_snapshot()
                await websocket.send_json({
                    "type": "OFFICE_UPDATE",
                    "event": mtype,
                    "agents": snap["agents"],
                })
        except (WebSocketDisconnect, json.JSONDecodeError):
            pass

    forwarder_task = asyncio.create_task(event_forwarder())
    listener_task = asyncio.create_task(client_listener())

    try:
        done, pending = await asyncio.wait(
            [forwarder_task, listener_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for t in pending:
            t.cancel()
    finally:
        await corporate_event_bus.unsubscribe(project_id, queue)
        logger.info(f"WebSocket Office terputus untuk [{project_id}]")
