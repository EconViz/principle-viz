"""Tax wedge renderer."""

from __future__ import annotations

from matplotlib.axes import Axes

from principle_viz.core.line import Line


def render_tax_wedge(
    ax: Axes,
    quantity: float,
    consumer_price: float,
    producer_price: float,
    color: str,
    label: str = "Tax wedge",
) -> None:
    """Render vertical tax wedge at the taxed equilibrium quantity."""
    ax.vlines(quantity, producer_price, consumer_price, color=color, linestyles="--", linewidth=2.0)
    ax.annotate(
        label,
        xy=(quantity, 0.5 * (consumer_price + producer_price)),
        xytext=(6, 0),
        textcoords="offset points",
        color=color,
        va="center",
    )


def render_tax_shift_arrow(
    ax: Axes,
    *,
    quantity: float,
    base_price: float,
    taxed_price: float,
    color: str,
    label: str,
) -> None:
    """Render vertical arrow from baseline point to taxed point at fixed quantity."""
    ax.annotate(
        "",
        xy=(quantity, taxed_price),
        xytext=(quantity, base_price),
        arrowprops={"arrowstyle": "->", "color": color, "lw": 1.8},
    )
    if label:
        ax.annotate(
            label,
            xy=(quantity, 0.5 * (base_price + taxed_price)),
            xytext=(8, 0),
            textcoords="offset points",
            color=color,
            va="center",
        )


def render_upward_tax_arrow(
    ax: Axes,
    *,
    quantity: float,
    base_price: float,
    taxed_price: float,
    color: str,
    label: str,
    bidirectional: bool = False,
) -> None:
    """Backward-compatible wrapper; prefer `render_tax_shift_arrow`."""
    _ = bidirectional
    render_tax_shift_arrow(
        ax,
        quantity=quantity,
        base_price=base_price,
        taxed_price=taxed_price,
        color=color,
        label=label,
    )


def render_rotation_arrow(
    ax: Axes,
    *,
    base_curve: Line,
    taxed_curve: Line,
    pivot_q: float,
    color: str,
    label: str,
    delta_q: float = 1.6,
) -> None:
    """Render a curved arrow that indicates a pivot/rotation around a fixed point."""
    start_q = pivot_q + delta_q
    end_q = pivot_q + 0.65 * delta_q
    start_p = base_curve.p_at(start_q)
    end_p = taxed_curve.p_at(end_q)

    ax.annotate(
        "",
        xy=(end_q, end_p),
        xytext=(start_q, start_p),
        arrowprops={
            "arrowstyle": "->",
            "color": color,
            "lw": 1.8,
            "connectionstyle": "arc3,rad=0.35",
        },
    )
    ax.annotate(
        label,
        xy=(end_q, end_p),
        xytext=(8, 8),
        textcoords="offset points",
        color=color,
    )
