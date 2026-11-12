"""Application settings with hard safety guards for paper-only mode."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LiveTradingForbiddenError(RuntimeError):
    """Raised when configuration attempts to enable real order execution."""


class Settings(BaseSettings):
    """Runtime configuration. Live trading is structurally forbidden in this version."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_mode: Literal["paper"] = "paper"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    market_data_provider: str = "binance_public"
    market_data_api_key: str = ""
    market_data_max_age_seconds: int = 120

    default_quote_asset: str = "USDT"
    default_symbols: str = "BTC/USDT,ETH/USDT"
    default_timeframe: str = "5m"

    paper_initial_balance: str = "100.00"
    paper_fee_rate: str = "0.001"
    paper_slippage_bps: int = 5

    trading_enabled: bool = False
    live_trading_enabled: bool = False

    @field_validator("live_trading_enabled")
    @classmethod
    def reject_live_trading_flag(cls, value: bool) -> bool:
        if value is True:
            raise ValueError(
                "LIVE_TRADING_ENABLED=true é proibido nesta versão. "
                "Somente paper trading é permitido."
            )
        return False

    @model_validator(mode="after")
    def enforce_paper_only(self) -> Settings:
        if self.app_mode != "paper":
            raise ValueError("APP_MODE deve ser 'paper' nesta versão.")
        if self.live_trading_enabled:
            raise LiveTradingForbiddenError(
                "Execução real de ordens é bloqueada nesta versão do Trading Bot."
            )
        return self

    @property
    def symbols(self) -> list[str]:
        return [s.strip() for s in self.default_symbols.split(",") if s.strip()]

    @property
    def public_settings(self) -> dict[str, object]:
        """Non-secret settings safe to expose via API."""
        return {
            "app_env": self.app_env,
            "app_mode": self.app_mode,
            "trading_enabled": self.trading_enabled,
            "live_trading_enabled": False,
            "default_quote_asset": self.default_quote_asset,
            "default_symbols": self.symbols,
            "default_timeframe": self.default_timeframe,
            "paper_initial_balance": self.paper_initial_balance,
            "paper_fee_rate": self.paper_fee_rate,
            "paper_slippage_bps": self.paper_slippage_bps,
            "market_data_provider": self.market_data_provider,
            "market_data_max_age_seconds": self.market_data_max_age_seconds,
            "simulation_banner": "PAPER TRADING — SEM DINHEIRO REAL",
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
