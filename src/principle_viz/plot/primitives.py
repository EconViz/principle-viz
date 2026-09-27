"""Shared low-level plotting primitives for renderers."""

from __future__ import annotations

from matplotlib.axes import Axes


def plot_point(
    ax: Axes,
    *,
    x: float,
    y: float,
    color: str,
    marker_size: float,
    marker: str = "o",
    linestyle: str = "None",
    zorder: int = 6,
) -> None:
    """Draw a point with consistent defaults."""
    ax.plot(
        x,
        y,
        marker=marker,
        linestyle=linestyle,
        color=color,
        markersize=marker_size,
        zorder=zorder,
        clip_on=False,
    )



def annotate_text(
    ax: Axes,
    *,
    x: float,
    y: float,
    text: str,
    color: str,
    offset: tuple[float, float] = (14, 14),
    fontsize: int = 11,
    curved_arrow: bool = True,
    curvature: float = 0.25,
) -> None:
    """Annotate text relative to a point."""
    arrowprops = None
    if curved_arrow:
        arrowprops = {
            "arrowstyle": "->",
            "color": color,
            "lw": 1.2,
            "connectionstyle": f"arc3,rad={curvature}",
            "shrinkA": 0,
            "shrinkB": 3,
        }
    ax.annotate(
        text,
        xy=(x, y),
        xytext=offset,
        textcoords="offset points",
        color=color,
        fontsize=fontsize,
        arrowprops=arrowprops,
    )
