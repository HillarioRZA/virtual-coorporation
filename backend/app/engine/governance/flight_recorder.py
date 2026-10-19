"""
Deterministic Agent Flight Recorder & Time-Travel Debugger.
Merekam alur keputusan agen, input/output mentah, dan transisi state dalam format append-only event stream.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from app.core.logger import logger


class FlightRecorderEvent:
    """Entitas data rekaman satu peristiwa transisi agen."""

    def __init__(
        self,
        project_id: str,
        event_type: str,
        agent_role: str,
        payload: Dict[str, Any],
        step_index: int = 0,
    ) -> None:
        """Inisialisasi FlightRecorderEvent."""
        self.event_id = f"evt_{uuid.uuid4().hex[:10]}"
        self.project_id = project_id
        self.timestamp = datetime.utcnow().isoformat()
        self.step_index = step_index
        self.event_type = event_type
        self.agent_role = agent_role
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """Konversi ke dictionary serializable."""
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "step_index": self.step_index,
            "event_type": self.event_type,
            "agent_role": self.agent_role,
            "payload": self.payload,
        }


class AgentFlightRecorder:
    """Perekam kotak hitam otonom (Black Box Flight Recorder) untuk multi-agent system."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi AgentFlightRecorder."""
        self.projects_dir = projects_dir or Path("projects_output")
        self._in_memory_logs: Dict[str, List[Dict[str, Any]]] = {}

    def record_step(
        self,
        project_id: str,
        event_type: str,
        agent_role: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mencatat satu langkah peristiwa ke dalam append-only stream."""
        if project_id not in self._in_memory_logs:
            self._in_memory_logs[project_id] = []

        step_idx = len(self._in_memory_logs[project_id]) + 1
        evt = FlightRecorderEvent(
            project_id=project_id,
            event_type=event_type,
            agent_role=agent_role,
            payload=payload,
            step_index=step_idx,
        )
        evt_dict = evt.to_dict()
        self._in_memory_logs[project_id].append(evt_dict)

        # Simpan secara asinkron ke file proyek jika folder proyek ada
        log_dir = self.projects_dir / project_id / ".flight_logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "flight_stream.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt_dict) + "\n")
        except OSError as err:
            logger.debug(f"Penyimpanan berkas flight log dilewati: {err}")

        return evt_dict

    def get_flight_log(self, project_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Mengambil seluruh riwayat peristiwa untuk time-travel replay dari penyimpanan persisten."""
        log_file = self.projects_dir / project_id / ".flight_logs" / "flight_stream.jsonl"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    file_logs = [json.loads(line) for line in f if line.strip()]
                    if file_logs:
                        self._in_memory_logs[project_id] = file_logs
                        return file_logs[-limit:]
            except (json.JSONDecodeError, OSError) as err:
                logger.debug(f"Error membaca persistent flight stream: {err}")
        return self._in_memory_logs.get(project_id, [])[-limit:]

    def replay_step(self, project_id: str, step_index: int) -> Optional[Dict[str, Any]]:
        """Mendapatkan snapshot state pada langkah tertentu untuk time-travel debugger."""
        logs = self.get_flight_log(project_id)
        for ev in logs:
            if ev.get("step_index") == step_index:
                return ev
        return None


agent_flight_recorder = AgentFlightRecorder()
