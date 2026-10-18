"""
Settings Constants and Metadata for Dynamic Settings Manager.
Berisi daftar kunci rahasia (sensitive), daftar penyedia AI, rekomendasi model, dan peran agen.
"""

from typing import Dict, List, Set

SENSITIVE_KEYS: Set[str] = {
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENAI_COMPATIBLE_API_KEY",
    "VAULT_MASTER_KEY",
    "APP_SECRET_KEY",
    "PAAS_API_TOKEN",
    "TELEGRAM_BOT_TOKEN",
}

AVAILABLE_PROVIDERS: List[str] = [
    "deepseek",
    "anthropic",
    "openai",
    "gemini",
    "openrouter",
    "ollama",
    "openai_compatible",
]

RECOMMENDED_MODELS: Dict[str, List[str]] = {
    "deepseek": ["deepseek-reasoner", "deepseek-chat"],
    "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
    "openai": ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
    "gemini": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"],
    "openrouter": [
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-2.0-flash-thinking-exp:free",
        "mistralai/mistral-small-24b-instruct-2501:free",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwen-2.5-coder-32b-instruct",
    ],
    "ollama": ["llama3.2", "qwen2.5-coder:7b", "mistral:latest", "deepseek-r1:8b"],
    "openai_compatible": ["qwen-2.5-coder-32b-instruct", "custom-model"],
}

SETTING_KEY_ALIASES: Dict[str, str] = {
    "TELEGRAM_AUTH_GATE_ENABLED": "AUTH_GATE_ENABLED",
    "TELEGRAM_ROTATION_HOURS": "AUTH_ROTATION_HOURS",
    "DOCKER_FRONTEND_IMAGE": "DOCKER_BASE_FRONTEND_IMAGE",
    "DOCKER_BACKEND_IMAGE": "DOCKER_BASE_BACKEND_IMAGE",
}

ROLE_METADATA: Dict[str, Dict[str, str]] = {
    "COS": {"title": "Chief of Staff (CoS)", "desc": "Evaluasi strategi bisnis, review PRD, dan sparring founder."},
    "CTO": {"title": "Chief Technology Officer (CTO)", "desc": "Arsitektur sistem, tech stack, dan validasi engineering."},
    "PM": {"title": "Product Manager (PM)", "desc": "Penajaman spesifikasi produk, user stories, dan spec freeze."},
    "UI_UX": {"title": "UI/UX Designer", "desc": "Perancangan user flow, layout wireframe, dan design tokens."},
    "FRONTEND": {"title": "Frontend Engineer", "desc": "Implementasi antarmuka interaktif React, Tailwind, Next.js."},
    "BACKEND": {"title": "Backend Engineer", "desc": "Implementasi endpoint REST FastAPI, model ORM, & migrasi."},
    "AI_DATA": {"title": "AI & Data Engineer", "desc": "Rekayasa prompt chains, evaluasi model, dan data pipeline."},
    "QA": {"title": "QA Engineer", "desc": "Audit keamanan OWASP Top 10, sanitasi input, dan scorecard."},
    "LEGAL": {"title": "Legal & Compliance", "desc": "Penyusunan berkas Terms of Service, Privacy, dan Refund."},
    "DEVSECOPS": {"title": "DevSecOps Engineer", "desc": "Packaging Docker Compose, webhook PaaS, dan live deploy."},
}
