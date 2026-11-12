"""FastAPI dependencies."""

from __future__ import annotations

from app.core.config import Settings, get_settings


def provide_settings() -> Settings:
    return get_settings()
