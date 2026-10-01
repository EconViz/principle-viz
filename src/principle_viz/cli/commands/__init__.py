"""CLI command registry."""

from __future__ import annotations

import argparse
from typing import Any, Protocol

from principle_viz.cli.commands import (
    elasticity,
    factor_markets,
    market,
    policy,
    ppf,
    public_goods,
    welfare,
)


class CommandModule(Protocol):
    def register(self, subparsers: Any) -> None: ...

    def handle(self, args: argparse.Namespace) -> bool: ...


COMMAND_MODULES: tuple[CommandModule, ...] = (
    market,
    policy,
    welfare,
    elasticity,
    public_goods,
    factor_markets,
    ppf,
)

__all__ = ["COMMAND_MODULES", "CommandModule"]
