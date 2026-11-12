"""Shared domain enums. Expandido nas fases de estratégia/execução."""

from __future__ import annotations

from enum import StrEnum


class SignalAction(StrEnum):
    BUY = "BUY"
    HOLD = "HOLD"
    EXIT = "EXIT"
    NO_TRADE = "NO_TRADE"
    KILL_SWITCH = "KILL_SWITCH"


class AppMode(StrEnum):
    PAPER = "paper"
