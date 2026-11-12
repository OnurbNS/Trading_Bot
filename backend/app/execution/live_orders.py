"""Bloqueio técnico absoluto de ordens reais — não implementar broker live nesta versão."""

from __future__ import annotations

from app.core.security import LiveOrderExecutionBlockedError, refuse_live_order


def submit_live_order(*args: object, **kwargs: object) -> None:
    """Qualquer tentativa de ordem real deve falhar de forma explícita."""
    refuse_live_order(*args, **kwargs)


__all__ = ["LiveOrderExecutionBlockedError", "submit_live_order"]
