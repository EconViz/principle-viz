"""Draw principle-viz's built-in figure text in English, Traditional or Simplified Chinese.

The words principle-viz puts in a figure ("Shortage", "Consumer surplus", panel titles, ...)
are English. With ``PlotTheme(language="zh-TW")`` or ``"zh-CN"`` each figure replaces them
with the translations in ``locale/labels.json``, the table the manual's Chinese editions use.
Text you set yourself, through ``labels=`` or ``configure_label``, is never translated.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Mapping
from functools import cache
from importlib import resources
from typing import TypeVar

LANGUAGES = ("en", "zh-TW", "zh-CN")

T = TypeVar("T")


def validate_language(language: str) -> str:
    """Return ``language`` if principle-viz can draw it, else raise ``ValueError``."""
    if language not in LANGUAGES:
        raise ValueError(
            f"language must be one of {', '.join(LANGUAGES)}; got {language!r}"
        )
    return language


@cache
def labels(language: str) -> Mapping[str, str]:
    """English text mapped to its translation; empty for English."""
    validate_language(language)
    if language == "en":
        return {}
    source = (
        resources.files("principle_viz.locale")
        .joinpath("labels.json")
        .read_text("utf-8")
    )
    table: dict[str, str] = json.loads(source)[language]
    return table


def translate(value: T, language: str) -> T:
    """``value`` with every built-in string replaced by its translation.

    Dataclasses (layers, specs, styles), tuples, lists and dicts are rebuilt only where
    something changed; anything else is returned as it is.
    """
    table = labels(language)
    return _translate(value, table) if table else value


def _translate(value, table):
    if isinstance(value, str):
        return table.get(value, value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        changes = {}
        for field in dataclasses.fields(value):
            if not field.init:
                continue
            old = getattr(value, field.name)
            new = _translate(old, table)
            if new is not old and new != old:
                changes[field.name] = new
        return dataclasses.replace(value, **changes) if changes else value
    if isinstance(value, tuple) and not hasattr(value, "_fields"):
        items = tuple(_translate(item, table) for item in value)
        return items if items != value else value
    if isinstance(value, list):
        return [_translate(item, table) for item in value]
    if isinstance(value, Mapping) and not isinstance(value, type):
        changed = {key: _translate(item, table) for key, item in value.items()}
        return changed if changed != dict(value) else value
    return value


__all__ = ["LANGUAGES", "labels", "translate", "validate_language"]
