"""Financial value helpers using Decimal (never float for money)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def money(value: str | int | Decimal) -> Decimal:
    """Parse a monetary/quantity value as Decimal."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Valor financeiro inválido: {value!r}") from exc
