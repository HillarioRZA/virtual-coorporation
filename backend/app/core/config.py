"""
Core System Configuration
Memuat dan memvalidasi konfigurasi lingkungan (.env) menggunakan Pydantic Settings.
"""

from typing import Dict, Tuple, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

# Lokasi root direktori proyek
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Core System Settings
    APP_ENV: str = Field(default="development", description="Environment: development | production")
    APP_SECRET_KEY: str = Field(default="insecure-dev-secret-key-change-in-production", description="Secret key for JWT")
    VAULT_MASTER_KEY: str = Field(default="U1RfV09SS19TVEFSVFVQX0FFU19LRVlfMzJCWT1=", description="AES-256 base64 key for Vault")
    BACKEND_HOST: str = Field(default="127.0.0.1")
    BACKEND_PORT: int = Field(default=8000)
    FRONTEND_PORT: int = Field(default=3000)
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/venture_memory.db")

    # Universal BYOK API Keys & Base URLs
    OPENAI_API_KEY: Optional[str] = Field(default="")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")

    DEEPSEEK_API_KEY: Optional[str] = Field(default="")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com/v1")

    ANTHROPIC_API_KEY: Optional[str] = Field(default="")
    ANTHROPIC_BASE_URL: str = Field(default="https://api.anthropic.com")

    GEMINI_API_KEY: Optional[str] = Field(default="")
    GEMINI_BASE_URL: str = Field(default="https://generativelanguage.googleapis.com/v1beta")

    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434/v1")

    OPENROUTER_API_KEY: Optional[str] = Field(default="")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")

    # Custom OpenAI-Compatible Provider (TokenomixAI, OpenRouter, vLLM, etc.)
    OPENAI_COMPATIBLE_API_KEY: Optional[str] = Field(default="")
    OPENAI_COMPATIBLE_BASE_URL: str = Field(default="https://api.tokenomixai.com/v1")
    OPENAI_COMPATIBLE_MODEL: str = Field(default="qwen-2.5-coder-32b-instruct")

    # Default Model Selection & Provider per Agent Role
    MODEL_COS: str = Field(default="deepseek-reasoner")
    PROVIDER_COS: str = Field(default="deepseek")

    MODEL_CTO: str = Field(default="claude-3-5-sonnet-20241022")
    PROVIDER_CTO: str = Field(default="anthropic")

    MODEL_PM: str = Field(default="gemini-2.5-flash")
    PROVIDER_PM: str = Field(default="gemini")

    MODEL_UI_UX: str = Field(default="claude-3-5-haiku-20241022")
    PROVIDER_UI_UX: str = Field(default="anthropic")

    MODEL_FRONTEND: str = Field(default="claude-3-5-sonnet-20241022")
    PROVIDER_FRONTEND: str = Field(default="anthropic")

    MODEL_BACKEND: str = Field(default="claude-3-5-sonnet-20241022")
    PROVIDER_BACKEND: str = Field(default="anthropic")

    MODEL_AI_DATA: str = Field(default="claude-3-5-sonnet-20241022")
    PROVIDER_AI_DATA: str = Field(default="anthropic")

    MODEL_QA: str = Field(default="deepseek-reasoner")
    PROVIDER_QA: str = Field(default="deepseek")

    MODEL_LEGAL: str = Field(default="deepseek-reasoner")
    PROVIDER_LEGAL: str = Field(default="deepseek")

    MODEL_DEVSECOPS: str = Field(default="qwen-2.5-coder-32b-instruct")
    PROVIDER_DEVSECOPS: str = Field(default="openai_compatible")

    # Ephemeral Sandbox & Reverse Proxy Settings
    SANDBOX_DOMAIN_SUFFIX: str = Field(default="local.sandbox")
    CADDY_ADMIN_API: str = Field(default="http://localhost:2019")
    DOCKER_BASE_FRONTEND_IMAGE: str = Field(default="venture-frontend-base:latest")
    DOCKER_BASE_BACKEND_IMAGE: str = Field(default="venture-backend-base:latest")
    DOCKER_CPU_LIMIT: float = Field(default=1.5, description="Batas hard quota core CPU untuk kontainer sandbox")
    DOCKER_MEMORY_LIMIT: str = Field(default="1024m", description="Batas hard quota RAM untuk kontainer sandbox")

    # PaaS Deployment Bridge
    PAAS_PROVIDER: str = Field(default="coolify")
    PAAS_API_URL: Optional[str] = Field(default="")
    PAAS_API_TOKEN: Optional[str] = Field(default="")

    # Personal Security Gate (Telegram Bot & Rotating Password)
    AUTH_GATE_ENABLED: bool = Field(default=False, description="Aktifkan gembok popup autentikasi Telegram")
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default="", description="Token bot Telegram dari @BotFather")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default="", description="ID chat Telegram dari @userinfobot")
    AUTH_ROTATION_HOURS: int = Field(default=6, description="Interval rotasi password otomatis dalam jam")

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_agent_model_and_provider(self, role: str) -> Tuple[str, str]:
        """Mengambil pasangan (model, provider) untuk peran agen tertentu."""
        role_map: Dict[str, Tuple[str, str]] = {
            "COS": (self.MODEL_COS, self.PROVIDER_COS),
            "CTO": (self.MODEL_CTO, self.PROVIDER_CTO),
            "PM": (self.MODEL_PM, self.PROVIDER_PM),
            "UI_UX": (self.MODEL_UI_UX, self.PROVIDER_UI_UX),
            "FRONTEND": (self.MODEL_FRONTEND, self.PROVIDER_FRONTEND),
            "BACKEND": (self.MODEL_BACKEND, self.PROVIDER_BACKEND),
            "AI_DATA": (self.MODEL_AI_DATA, self.PROVIDER_AI_DATA),
            "QA": (self.MODEL_QA, self.PROVIDER_QA),
            "LEGAL": (self.MODEL_LEGAL, self.PROVIDER_LEGAL),
            "DEVSECOPS": (self.MODEL_DEVSECOPS, self.PROVIDER_DEVSECOPS),
        }
        return role_map.get(role.upper(), (self.MODEL_CTO, self.PROVIDER_CTO))

# Singleton instance
settings = Settings()
