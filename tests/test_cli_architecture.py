from __future__ import annotations

import argparse
import ast
from pathlib import Path

from principle_viz.cli.commands import COMMAND_MODULES
from principle_viz.cli.main import build_parser

CLI_ROOT = Path(__file__).parents[1] / "src" / "principle_viz" / "cli"


def test_each_cli_command_has_exactly_one_owner() -> None:
    commands = [command for module in COMMAND_MODULES for command in module.COMMANDS]
    assert len(commands) == len(set(commands))

    parser = build_parser()
    subparsers = next(
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    assert set(subparsers.choices) == set(commands)


def test_cli_main_is_only_a_composition_root() -> None:
    path = CLI_ROOT / "main.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert len(path.read_text(encoding="utf-8").splitlines()) <= 40
    assert imported_modules == {
        "__future__",
        "principle_viz.cli.commands",
    }


def test_cli_commands_are_grouped_by_domain() -> None:
    expected = {
        "elasticity.py",
        "factor_markets.py",
        "market.py",
        "policy.py",
        "ppf.py",
        "public_goods.py",
        "welfare.py",
    }
    assert expected.issubset(
        {path.name for path in (CLI_ROOT / "commands").glob("*.py")}
    )
