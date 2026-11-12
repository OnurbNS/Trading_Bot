"""Health check endpoint."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.api.dependencies import provide_settings
from app.core.config import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Annotated[Settings, Depends(provide_settings)]) -> dict[str, object]:
    return {
        "status": "ok",
        "service": "trading-bot-backend",
        "version": __version__,
        "app_env": settings.app_env,
        "app_mode": settings.app_mode,
        "trading_enabled": settings.trading_enabled,
        "live_trading_enabled": False,
        "simulation": "PAPER TRADING — SEM DINHEIRO REAL",
        "timestamp": datetime.now(UTC).isoformat(),
    }
