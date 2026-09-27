"""Metrics text-box renderer."""

from __future__ import annotations

from matplotlib.axes import Axes

_LOCATIONS: dict[str, tuple[float, float, str, str]] = {
    "upper right": (0.98, 0.98, "right", "top"),
    "upper left": (0.02, 0.98, "left", "top"),
    "lower right": (0.98, 0.02, "right", "bottom"),
    "lower left": (0.02, 0.02, "left", "bottom"),
}



def _format_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)



def render_metrics_box(
    ax: Axes,
    metrics: dict[str, object],
    *,
    title: str | None = None,
    location: str = "upper right",
    text_color: str = "#222222",
    edge_color: str = "#222222",
    face_color: str = "#FFFFFF",
    alpha: float = 0.9,
    fontsize: int = 10,
) -> None:
    """Render key-value metrics as a square-corner info box in axes coords."""
    x, y, ha, va = _LOCATIONS.get(location, _LOCATIONS["upper right"])

    lines: list[str] = []
    if title:
        lines.append(title)
        lines.append("-")
    lines.extend(f"{k}: {_format_metric(v)}" for k, v in metrics.items())

    ax.text(
        x,
        y,
        "\n".join(lines),
        transform=ax.transAxes,
        ha=ha,
        va=va,
        color=text_color,
        fontsize=fontsize,
        bbox={
            "boxstyle": "square,pad=0.35",
            "facecolor": face_color,
            "edgecolor": edge_color,
            "alpha": alpha,
            "linewidth": 1.0,
        },
    )
