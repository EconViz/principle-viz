"""Welfare polygon renderer."""

from __future__ import annotations

from matplotlib.axes import Axes

from principle_viz.welfare.layout import (
    WelfareAnnotationLayout,
    build_welfare_annotation_layout,
)
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


def _fill_polygon(ax: Axes, points: tuple[tuple[float, float], ...], color: str, label: str, alpha: float) -> None:
    if not points:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.fill(xs, ys, color=color, alpha=alpha, label=label)



def render_surplus_regions(
    ax: Axes,
    surplus: SurplusResult,
    cs_color: str,
    ps_color: str,
    tax_color: str,
    dwl_color: str,
) -> None:
    """Render welfare-related polygons."""
    _fill_polygon(ax, surplus.polygons.consumer_surplus, cs_color, "Consumer Surplus", alpha=0.18)
    _fill_polygon(ax, surplus.polygons.producer_surplus, ps_color, "Producer Surplus", alpha=0.18)
    _fill_polygon(ax, surplus.polygons.tax_revenue, tax_color, "Tax Revenue", alpha=0.22)
    _fill_polygon(ax, surplus.polygons.lost_surplus, dwl_color, "Deadweight Loss", alpha=0.22)


def render_welfare_reference_lines(
    ax: Axes,
    *,
    layout: WelfareAnnotationLayout,
    color: str,
    linewidth: float = 1.0,
) -> None:
    """Render baseline/policy price-quantity guide lines."""
    ref = layout.reference

    ax.vlines(
        ref.baseline_quantity,
        0.0,
        ref.baseline_price,
        colors=color,
        linestyles=":",
        linewidth=linewidth,
    )
    ax.hlines(
        ref.baseline_price,
        0.0,
        ref.baseline_quantity,
        colors=color,
        linestyles=":",
        linewidth=linewidth,
    )

    policy_top_price = max(ref.policy_consumer_price, ref.policy_producer_price)
    ax.vlines(
        ref.policy_quantity,
        0.0,
        policy_top_price,
        colors=color,
        linestyles="--",
        linewidth=linewidth,
    )
    ax.hlines(
        ref.policy_consumer_price,
        0.0,
        ref.policy_quantity,
        colors=color,
        linestyles="--",
        linewidth=linewidth,
    )
    if abs(ref.policy_consumer_price - ref.policy_producer_price) > 1e-9:
        ax.hlines(
            ref.policy_producer_price,
            0.0,
            ref.policy_quantity,
            colors=color,
            linestyles="--",
            linewidth=linewidth,
        )

    ax.annotate(
        r"$Q_0$",
        xy=(ref.baseline_quantity, 0.0),
        xytext=(0, -12),
        textcoords="offset points",
        ha="center",
        va="top",
        color=color,
    )
    ax.annotate(
        r"$Q_1$",
        xy=(ref.policy_quantity, 0.0),
        xytext=(0, -12),
        textcoords="offset points",
        ha="center",
        va="top",
        color=color,
    )
    ax.annotate(
        r"$P_0$",
        xy=(0.0, ref.baseline_price),
        xytext=(-12, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=color,
    )
    ax.annotate(
        r"$P_1^c$",
        xy=(0.0, ref.policy_consumer_price),
        xytext=(-12, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=color,
    )
    if abs(ref.policy_consumer_price - ref.policy_producer_price) > 1e-9:
        ax.annotate(
            r"$P_1^p$",
            xy=(0.0, ref.policy_producer_price),
            xytext=(-12, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            color=color,
        )


def render_region_letters(
    ax: Axes,
    *,
    layout: WelfareAnnotationLayout,
    color: str,
) -> None:
    """Annotate region letters and definitions."""
    for region in layout.regions:
        x, y = region.centroid
        ax.text(
            x,
            y,
            region.letter,
            color=color,
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
        )

    if not layout.regions:
        return

    legend_lines = [f"{region.letter}: {region.label}" for region in layout.regions]
    ax.text(
        0.02,
        0.98,
        "\n".join(legend_lines),
        transform=ax.transAxes,
        ha="left",
        va="top",
        color=color,
        fontsize=9,
    )


def render_welfare_overlay(
    ax: Axes,
    *,
    baseline_outcome: MarketOutcome,
    policy_outcome: MarketOutcome,
    surplus: SurplusResult,
    color: str,
) -> WelfareAnnotationLayout:
    """Render guide lines + letter labels for welfare decomposition."""
    layout = build_welfare_annotation_layout(
        baseline_outcome=baseline_outcome,
        policy_outcome=policy_outcome,
        surplus=surplus,
    )
    render_welfare_reference_lines(ax, layout=layout, color=color)
    render_region_letters(ax, layout=layout, color=color)
    return layout
