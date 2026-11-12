"""MarketDataProvider protocol — estrutura preparada; implementação na Fase 3."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class MarketDataProvider(Protocol):
    """Interface substituível para provedores de dados de mercado."""

    def list_symbols(self) -> list[str]:
        """Lista símbolos suportados pelo provedor."""
        ...

    def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        *,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, object]]:
        """Busca candles históricos (contrato a detalhar na Fase 3)."""
        ...
