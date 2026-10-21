"""
Venture Engine Corporate Subsystem.
Modular multi-agent operating engine, dikategorikan ke dalam sub-paket:
- roles: Dynamic role executor & output handlers
- runtime: Asynchronous dispatcher, event bus, state machine, worker pool
- governance: Circuit breaker, financial guardrails, flight recorder, branch merger
- memory: SQLite blackboard, vector memory, episodic memory, institutional wisdom
- quality: Security scanner, peer reviewer, static preflight checks, evaluators
- office: Oasis live command HQ, chat console, 2D office layout & simulator
- schemas: Venture contracts, role DTOs, workflow DTOs, output envelopes
- tools: Agent tool implementations, dispatchers, synthesizer, code bundle writer
- sentinel: Chain-of-Verification (CoV) observability & pre-flight gatekeeper
"""

import importlib
import sys

# Subpackage Modules Mapping untuk backward compatibility
_FORWARDING_MODULES = {
    "dynamic_node": "app.engine.roles.dynamic_node",
    "role_output_processor": "app.engine.roles.role_output_processor",
    "role_event_logger": "app.engine.roles.role_event_logger",
    "mention_relay": "app.engine.roles.mention_relay",
    "org_context": "app.engine.roles.org_context",

    "state": "app.engine.runtime.state",
    "dispatcher": "app.engine.runtime.dispatcher",
    "event_bus": "app.engine.runtime.event_bus",
    "state_machine": "app.engine.runtime.state_machine",
    "checkpointer": "app.engine.runtime.checkpointer",
    "autonomous_healer": "app.engine.runtime.autonomous_healer",
    "speculative_branch": "app.engine.runtime.speculative_branch",
    "model_router": "app.engine.runtime.model_router",
    "worker_pool": "app.engine.runtime.worker_pool",
    "routers": "app.engine.runtime.routers",

    "circuit_breaker": "app.engine.governance.circuit_breaker",
    "financial_guardrail": "app.engine.governance.financial_guardrail",
    "flight_recorder": "app.engine.governance.flight_recorder",
    "branch_merge": "app.engine.governance.branch_merge",

    "episodic_memory": "app.engine.memory.episodic_memory",
    "vector_store": "app.engine.memory.vector_store",
    "context_builder": "app.engine.memory.context_builder",
    "state_handoff": "app.engine.memory.state_handoff",
    "wisdom_engine": "app.engine.memory.wisdom_engine",

    "security_scanner": "app.engine.quality.security_scanner",
    "security_finding": "app.engine.quality.security_finding",
    "peer_reviewer": "app.engine.quality.peer_reviewer",
    "preflight_auditor": "app.engine.quality.preflight_auditor",
    "semantic_linter": "app.engine.quality.semantic_linter",
    "visual_evaluator": "app.engine.quality.visual_evaluator",
    "citation_auditor": "app.engine.quality.citation_auditor",
    "editorial_reviewer": "app.engine.quality.editorial_reviewer",
    "diff_engine": "app.engine.quality.diff_engine",

    "office_dispatch": "app.engine.office.office_dispatch",
    "office_simulator": "app.engine.office.office_simulator",

    "corporate_schemas": "app.engine.schemas.corporate_schemas",
    "workflow_schemas": "app.engine.schemas.workflow_schemas",
    "envelope_schemas": "app.engine.schemas.envelope_schemas",

    "agent_tool_dispatcher": "app.engine.tools.agent_tool_dispatcher",
    "ast_patcher": "app.engine.tools.ast_patcher",
    "tool_synthesizer": "app.engine.tools.tool_synthesizer",
    "artifact_compiler": "app.engine.tools.artifact_compiler",
    "design_token_engine": "app.engine.tools.design_token_engine",
    "github_bridge": "app.engine.tools.github_bridge",
    "scaffolding": "app.engine.tools.scaffolding",
}

for _sub_name, _target_path in _FORWARDING_MODULES.items():
    _full_old = f"app.engine.{_sub_name}"
    try:
        _mod = importlib.import_module(_target_path)
        sys.modules[_full_old] = _mod
    except Exception:
        pass

# Re-export core abstractions
from app.engine.runtime.state import VentureState
from app.engine.roles.dynamic_node import execute_dynamic_role_node
from app.engine.runtime.dispatcher import task_dispatcher
dispatcher = task_dispatcher
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.memory.memory import MemoryManager
from app.engine.memory.wisdom_engine import wisdom_engine
from app.engine.governance.circuit_breaker import agent_circuit_breaker
circuit_breaker = agent_circuit_breaker

__all__ = [
    "VentureState",
    "execute_dynamic_role_node",
    "task_dispatcher",
    "dispatcher",
    "corporate_event_bus",
    "MemoryManager",
    "wisdom_engine",
    "agent_circuit_breaker",
    "circuit_breaker",
]
