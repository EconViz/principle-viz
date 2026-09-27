"""Equilibrium point and movement renderers."""

from __future__ import annotations

from matplotlib.axes import Axes

from principle_viz.core.equilibrium import EquilibriumResult
from principle_viz.plot.primitives import annotate_text, plot_point


def render_equilibrium_point(
    ax: Axes,
    equilibrium: EquilibriumResult,
    label: str,
    color: str,
    marker_size: float = 6.0,
    curvature: float = 0.25,
) -> None:
    """Render equilibrium point and text label."""
    plot_point(
        ax,
        x=equilibrium.q_star,
        y=equilibrium.p_star,
        color=color,
        marker_size=marker_size,
    )
    annotate_text(
        ax,
        x=equilibrium.q_star,
        y=equilibrium.p_star,
        text=label,
        color=color,
        curved_arrow=True,
        curvature=curvature,
    )



def render_movement_arrows(
    ax: Axes,
    baseline: EquilibriumResult,
    shifted: EquilibriumResult,
    color: str,
    linewidth: float = 1.6,
) -> None:
    """Render right/left then up/down movement arrows."""
    ax.annotate(
        "",
        xy=(shifted.q_star, baseline.p_star),
        xytext=(baseline.q_star, baseline.p_star),
        arrowprops={"arrowstyle": "->", "color": color, "lw": linewidth},
    )
    ax.annotate(
        "",
        xy=(shifted.q_star, shifted.p_star),
        xytext=(shifted.q_star, baseline.p_star),
        arrowprops={"arrowstyle": "->", "color": color, "lw": linewidth},
    )
