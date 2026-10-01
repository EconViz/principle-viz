"""Shared helpers for example scripts."""

from __future__ import annotations

import shutil
from pathlib import Path

OUTPUT_DIR = Path("examples/output")
EXAMPLE_PALETTE = "monochrome"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".pdf"}


def ensure_output_dir(theme: str | None = None) -> Path:
    """Create output directory (optionally themed) and return it."""
    target = OUTPUT_DIR / theme if theme else OUTPUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def themed_output_path(theme: str, filename: str) -> Path:
    """Build a themed output path under examples/output/<theme>/."""
    return ensure_output_dir(theme) / filename


def remove_non_image_outputs() -> None:
    """Delete non-image files from output directory recursively."""
    ensure_output_dir()
    for item in OUTPUT_DIR.rglob("*"):
        if (
            item.is_file()
            and item.name != ".gitkeep"
            and item.suffix.lower() not in IMAGE_SUFFIXES
        ):
            item.unlink()


def clear_all_outputs() -> None:
    """Remove the full examples/output tree, then recreate it."""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / ".gitkeep").touch()
