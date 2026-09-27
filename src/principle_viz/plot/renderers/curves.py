"""Curve rendering primitives."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from principle_viz.core.line import Line


def render_curve(
    ax: Axes,
    line: Line,
    q_min: float,
    q_max: float,
    label: str,
    color: str,
    linestyle: str = "-",
    linewidth: float = 2.0,
    points: int = 200,
) -> None:
    """Render inverse-demand/supply curve in P-Q space."""
    qs = np.linspace(float(q_min), float(q_max), int(points))
    ps = np.array([line.p_at(q) for q in qs])
    ax.plot(qs, ps, label=label, color=color, linestyle=linestyle, linewidth=linewidth)
