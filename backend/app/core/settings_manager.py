"""
Dynamic Settings Manager.
Mengelola override konfigurasi sistem secara runtime, persistensi ke SQLite,
dan sanitasi nilai kredensial rahasia (masking).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import aiosqlite

from app.core.config import ENV_FILE, Settings, settings
from app.core.logger import logger
from app.core.settings_constants import (
    AVAILABLE_PROVIDERS,
    RECOMMENDED_MODELS,
    ROLE_METADATA,
    SENSITIVE_KEYS,
    SETTING_KEY_ALIASES,
)
from app.db.session import get_db_connection


class DynamicSettingsManager:
    """Manajer konfigurasi sistem dinamis yang tersinkronisasi dengan SQLite."""

    @staticmethod
    def mask_secret(value: Optional[str]) -> str:
        """Menyembunyikan karakter rahasia API key untuk eksposur UI aman."""
        if not value:
            return ""
        if len(value) <= 8:
            return "********"
        return f"{value[:3]}...{value[-4:]}"

    async def load_overrides(self, custom_path: Optional[str] = None) -> None:
        """Memuat seluruh nilai override dari basis data SQLite ke runtime settings."""
        try:
            async with get_db_connection(custom_path) as conn:
                cursor = await conn.execute("SELECT key, value FROM system_settings;")
                rows = await cursor.fetchall()
                for row in rows:
                    raw_key, val = row["key"], row["value"]
                    key = SETTING_KEY_ALIASES.get(raw_key, raw_key)
                    if hasattr(settings, key):
                        field_info = type(settings).model_fields.get(key)
                        if field_info and field_info.annotation is int:
                            setattr(settings, key, int(val))
                        elif field_info and field_info.annotation is bool:
                            setattr(settings, key, str(val).lower() in ("true", "1", "yes"))
                        else:
                            setattr(settings, key, val)
                logger.info(f"Berhasil memuat {len(rows)} konfigurasi dinamis dari SQLite.")
        except Exception as err:
            logger.warning(f"Gagal memuat dynamic settings dari SQLite: {err}")

    def get_runtime_settings(self) -> Dict[str, Any]:
        """Mengambil data konfigurasi saat ini dikelompokkan berdasarkan kategori."""
        roles_config: Dict[str, Dict[str, Any]] = {}
        for role, meta in ROLE_METADATA.items():
            model_attr = f"MODEL_{role}"
            provider_attr = f"PROVIDER_{role}"
            roles_config[role] = {
                "title": meta["title"],
                "desc": meta["desc"],
                "model": getattr(settings, model_attr, ""),
                "provider": getattr(settings, provider_attr, ""),
            }

        providers_config: Dict[str, Dict[str, Any]] = {
            "openai": {"key": self.mask_secret(settings.OPENAI_API_KEY), "base_url": settings.OPENAI_BASE_URL, "is_set": bool(settings.OPENAI_API_KEY)},
            "deepseek": {"key": self.mask_secret(settings.DEEPSEEK_API_KEY), "base_url": settings.DEEPSEEK_BASE_URL, "is_set": bool(settings.DEEPSEEK_API_KEY)},
            "anthropic": {"key": self.mask_secret(settings.ANTHROPIC_API_KEY), "base_url": settings.ANTHROPIC_BASE_URL, "is_set": bool(settings.ANTHROPIC_API_KEY)},
            "gemini": {"key": self.mask_secret(settings.GEMINI_API_KEY), "base_url": settings.GEMINI_BASE_URL, "is_set": bool(settings.GEMINI_API_KEY)},
            "openrouter": {"key": self.mask_secret(settings.OPENROUTER_API_KEY), "base_url": settings.OPENROUTER_BASE_URL, "is_set": bool(settings.OPENROUTER_API_KEY)},
            "ollama": {"key": "", "base_url": settings.OLLAMA_BASE_URL, "is_set": True},
            "openai_compatible": {
                "key": self.mask_secret(getattr(settings, "OPENAI_COMPATIBLE_API_KEY", "")),
                "base_url": getattr(settings, "OPENAI_COMPATIBLE_BASE_URL", "https://api.tokenomixai.com/v1"),
                "model": getattr(settings, "OPENAI_COMPATIBLE_MODEL", "qwen-2.5-coder-32b-instruct"),
                "is_set": bool(getattr(settings, "OPENAI_COMPATIBLE_API_KEY", "")),
            },
        }

        system_config = {
            "app_env": settings.APP_ENV,
            "backend_host": settings.BACKEND_HOST,
            "backend_port": settings.BACKEND_PORT,
            "frontend_port": settings.FRONTEND_PORT,
            "database_url": settings.DATABASE_URL,
        }

        paas_config = {
            "provider": settings.PAAS_PROVIDER,
            "api_url": settings.PAAS_API_URL or "",
            "api_token": self.mask_secret(settings.PAAS_API_TOKEN),
            "is_token_set": bool(settings.PAAS_API_TOKEN),
        }

        sandbox_config = {
            "domain_suffix": settings.SANDBOX_DOMAIN_SUFFIX,
            "caddy_admin_api": settings.CADDY_ADMIN_API,
            "frontend_image": settings.DOCKER_BASE_FRONTEND_IMAGE,
            "backend_image": settings.DOCKER_BASE_BACKEND_IMAGE,
        }

        telegram_config = {
            "auth_gate_enabled": bool(getattr(settings, "AUTH_GATE_ENABLED", False)),
            "bot_token": self.mask_secret(getattr(settings, "TELEGRAM_BOT_TOKEN", "")),
            "is_token_set": bool(getattr(settings, "TELEGRAM_BOT_TOKEN", "")),
            "chat_id": getattr(settings, "TELEGRAM_CHAT_ID", "") or "",
            "rotation_hours": int(getattr(settings, "AUTH_ROTATION_HOURS", 6)),
        }

        return {
            "roles": roles_config,
            "providers": providers_config,
            "system": system_config,
            "paas": paas_config,
            "sandbox": sandbox_config,
            "telegram": telegram_config,
            "available_providers": AVAILABLE_PROVIDERS,
            "recommended_models": RECOMMENDED_MODELS,
        }

    async def update_runtime_settings(self, updates: Dict[str, Any], custom_path: Optional[str] = None) -> int:
        """Memperbarui konfigurasi runtime in-memory dan menyimpannya ke tabel SQLite."""
        updated_count = 0
        async with get_db_connection(custom_path) as conn:
            for raw_key, val in updates.items():
                key = SETTING_KEY_ALIASES.get(raw_key, raw_key)
                if not hasattr(settings, key):
                    continue
                if key in SENSITIVE_KEYS and ("..." in str(val) or str(val) == "********"):
                    continue

                field_info = type(settings).model_fields.get(key)
                if field_info and field_info.annotation is int:
                    cast_val = int(val)
                elif field_info and field_info.annotation is bool:
                    cast_val = bool(val) if isinstance(val, bool) else (str(val).lower() in ("true", "1", "yes"))
                else:
                    cast_val = str(val)

                setattr(settings, key, cast_val)

                category = "role" if key.startswith(("MODEL_", "PROVIDER_")) else "credentials" if key in SENSITIVE_KEYS else "system"
                await conn.execute(
                    """
                    INSERT INTO system_settings (key, value, category, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP;
                    """,
                    (key, str(cast_val), category),
                )
                updated_count += 1
            await conn.commit()
        logger.info(f"Berhasil memperbarui {updated_count} konfigurasi dinamis.")
        return updated_count

    async def reset_to_defaults(self, custom_path: Optional[str] = None) -> None:
        """Menghapus seluruh override dari SQLite dan mengembalikan setting dari default .env."""
        async with get_db_connection(custom_path) as conn:
            await conn.execute("DELETE FROM system_settings;")
            await conn.commit()
        fresh_settings = Settings()
        for field in Settings.model_fields:
            setattr(settings, field, getattr(fresh_settings, field))
        logger.info("Konfigurasi sistem berhasil di-reset ke nilai default.")


dynamic_settings_manager = DynamicSettingsManager()
