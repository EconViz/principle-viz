"""Price control renderer."""

from __future__ import annotations

from matplotlib.axes import Axes

from principle_viz.core.controls import PriceControlResult


def render_control_line(ax: Axes, result: PriceControlResult, color: str) -> None:
    """Render control line with basic binding annotation."""
    ax.axhline(result.control_price, color=color, linestyle="--", linewidth=1.8, label=result.control_type.value.title())
    if result.is_binding:
        note = f"Binding ({result.control_type.value})"
    else:
        note = f"Non-binding ({result.control_type.value})"
    ax.annotate(note, xy=(0.02, 0.96), xycoords="axes fraction", ha="left", va="top", color=color)
