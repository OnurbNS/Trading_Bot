"""Config and live-trading hard-block tests."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import Settings, reset_settings_cache
from app.core.security import LiveOrderExecutionBlockedError, assert_paper_only, refuse_live_order
from app.domain.value_objects import money
from app.execution.live_orders import submit_live_order


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    reset_settings_cache()
    yield
    reset_settings_cache()


def test_settings_default_is_paper_and_live_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LIVE_TRADING_ENABLED", raising=False)
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("TRADING_ENABLED", raising=False)
    settings = Settings()
    assert settings.app_mode == "paper"
    assert settings.live_trading_enabled is False
    assert settings.trading_enabled is False


def test_live_trading_enabled_true_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "true")
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    message = str(exc_info.value)
    assert "LIVE_TRADING_ENABLED" in message or "proibido" in message.lower()


def test_app_mode_live_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_MODE", "live")
    with pytest.raises(ValidationError):
        Settings()


def test_app_mode_invalid_value_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_MODE", "production-trading")
    with pytest.raises(ValidationError):
        Settings()


def test_assert_paper_only_passes_for_defaults() -> None:
    settings = Settings()
    assert_paper_only(settings)


def test_submit_live_order_always_raises() -> None:
    with pytest.raises(LiveOrderExecutionBlockedError):
        submit_live_order(symbol="BTC/USDT", quantity="1")


def test_refuse_live_order_always_raises() -> None:
    with pytest.raises(LiveOrderExecutionBlockedError):
        refuse_live_order(side="BUY")


def test_money_uses_decimal_not_float() -> None:
    value = money("100.10")
    assert isinstance(value, Decimal)
    assert value == Decimal("100.10")
    assert value + Decimal("0.01") == Decimal("100.11")


def test_money_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        money("not-a-number")
