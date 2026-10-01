"""Thin CLI composition root for principle_viz."""

from __future__ import annotations

import argparse

from principle_viz.cli.commands import COMMAND_MODULES


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser from independently owned command modules."""
    parser = argparse.ArgumentParser(prog="principle-viz")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command_module in COMMAND_MODULES:
        command_module.register(subparsers)
    return parser


def main() -> None:
    """Parse and dispatch one CLI command."""
    parser = build_parser()
    args = parser.parse_args()
    for command_module in COMMAND_MODULES:
        if command_module.handle(args):
            return
    parser.error(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
