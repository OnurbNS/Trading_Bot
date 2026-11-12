"""Security helpers. Live order execution is structurally unavailable."""

from __future__ import annotations

from app.core.config import Settings


class LiveOrderExecutionBlockedError(RuntimeError):
    """No code path may send real exchange orders in this version."""


def assert_paper_only(settings: Settings) -> None:
    """Hard guard used at startup and before any execution path."""
    if settings.live_trading_enabled or settings.app_mode != "paper":
        raise LiveOrderExecutionBlockedError(
            "Bloqueio técnico absoluto: envio de ordens reais não existe nesta versão."
        )


def refuse_live_order(*_args: object, **_kwargs: object) -> None:
    """Placeholder that must never be replaced by a real broker client in Phase 1–8."""
    raise LiveOrderExecutionBlockedError(
        "Envio de ordens reais é proibido. Use apenas o paper broker (Fases posteriores)."
    )
