"""
Authentication & Telegram Gate API Router.
Menyediakan endpoint untuk verifikasi password dinamis, status autentikasi,
serta pengiriman ulang dan rotasi password via Telegram Bot API.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.core.auth_manager import auth_manager
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Personal Security Gate"])


class VerifyPasswordRequest(BaseModel):
    """Payload verifikasi password popup dinamis."""
    password: str = Field(..., min_length=1, description="Password akses yang dikirim ke Telegram.")


@router.get("/status", response_model=Dict[str, Any])
async def get_auth_status(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Mengecek status gembok keamanan dan keabsahan token sesi aktif."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()

    is_enabled = auth_manager.is_enabled()
    is_authenticated = auth_manager.verify_session_token(token) if is_enabled else True

    exp_str = auth_manager.expires_at.isoformat() if auth_manager.expires_at else None
    return {
        "status": "success",
        "data": {
            "is_enabled": is_enabled,
            "is_authenticated": is_authenticated,
            "expires_at": exp_str,
            "rotation_hours": auth_manager.get_rotation_hours(),
        },
    }


@router.post("/verify", response_model=Dict[str, Any])
async def verify_password(payload: VerifyPasswordRequest) -> Dict[str, Any]:
    """Memverifikasi password dinamis dan menerbitkan session token jika cocok."""
    is_valid = auth_manager.verify_password(payload.password)
    if not is_valid:
        logger.warning("Percobaan otentikasi ditolak: kode salah atau telah kedaluwarsa.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kode akses tidak valid atau telah kedaluwarsa.",
        )

    session_token = auth_manager.create_session_token()
    return {
        "status": "success",
        "message": "Autentikasi berhasil.",
        "data": {
            "session_token": session_token,
            "expires_at": auth_manager.expires_at.isoformat() if auth_manager.expires_at else None,
        },
    }


@router.post("/resend", response_model=Dict[str, Any])
async def resend_password(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Mengirim ulang password aktif saat ini ke Telegram pengguna (memerlukan otentikasi sesi aktif)."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()

    if auth_manager.is_enabled() and not auth_manager.verify_session_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Tindakan ini memerlukan otentikasi sesi yang valid.",
        )

    if not auth_manager.active_password:
        auth_manager.generate_new_password()

    success, message = await auth_manager.dispatch_to_telegram(reason="PERMINTAAN ADMIN")
    return {
        "status": "success" if success else "warning",
        "message": message,
    }


@router.post("/rotate", response_model=Dict[str, Any])
async def rotate_password(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Memaksa rotasi password baru seketika dan mengirimkannya ke Telegram (memerlukan otentikasi sesi aktif)."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()

    if auth_manager.is_enabled() and not auth_manager.verify_session_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Tindakan ini memerlukan otentikasi sesi yang valid.",
        )

    new_pw = auth_manager.generate_new_password()
    success, message = await auth_manager.dispatch_to_telegram(new_pw, reason="ROTASI MANUAL (ADMIN TRIGGER)")
    return {
        "status": "success" if success else "warning",
        "message": message,
        "data": {
            "expires_at": auth_manager.expires_at.isoformat() if auth_manager.expires_at else None,
        },
    }

