"""
System Settings API Endpoints.
Menyediakan endpoint untuk membaca, memutakhirkan, dan mereset konfigurasi runtime
multi-agent system tanpa memerlukan restart server atau perubahan kode.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.settings_manager import dynamic_settings_manager

router = APIRouter(prefix="/settings", tags=["System Settings"])


class UpdateSettingsRequest(BaseModel):
    """Payload pemutakhiran konfigurasi sistem dinamis."""
    updates: Dict[str, Any] = Field(
        ...,
        description="Pasangan key-value pengaturan yang ingin dimutakhirkan.",
        json_schema_extra={"example": {"MODEL_COS": "deepseek-reasoner", "PROVIDER_COS": "deepseek"}},
    )


@router.get("", response_model=Dict[str, Any])
async def get_settings() -> Dict[str, Any]:
    """Mengambil konfigurasi sistem aktif saat ini beserta metadata provider dan model."""
    try:
        data = dynamic_settings_manager.get_runtime_settings()
        return {"status": "success", "data": data}
    except Exception as err:
        logger.error(f"Gagal mengambil pengaturan sistem: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil pengaturan: {str(err)}",
        )


@router.put("", response_model=Dict[str, Any])
async def update_settings(payload: UpdateSettingsRequest) -> Dict[str, Any]:
    """Menyimpan pemutakhiran konfigurasi sistem dinamis secara instan ke SQLite dan runtime."""
    try:
        updated_count = await dynamic_settings_manager.update_runtime_settings(payload.updates)
        current = dynamic_settings_manager.get_runtime_settings()
        return {
            "status": "success",
            "message": f"{updated_count} pengaturan berhasil diperbarui.",
            "data": current,
        }
    except Exception as err:
        logger.error(f"Gagal memperbarui pengaturan sistem: {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal memperbarui pengaturan: {str(err)}",
        )


@router.post("/reset", response_model=Dict[str, Any])
async def reset_settings() -> Dict[str, Any]:
    """Mereset seluruh override pengaturan kembali ke nilai default dari berkas .env."""
    try:
        await dynamic_settings_manager.reset_to_defaults()
        current = dynamic_settings_manager.get_runtime_settings()
        return {
            "status": "success",
            "message": "Pengaturan sistem berhasil dikembalikan ke default.",
            "data": current,
        }
    except Exception as err:
        logger.error(f"Gagal mereset pengaturan sistem: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mereset pengaturan: {str(err)}",
        )
