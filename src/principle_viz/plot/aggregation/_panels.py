"""Panel specs and the shared builder for aggregation figures."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from itertools import pairwise

from mosaickit import Canvas, DashStyle, GridLink, Layer, Stroke

from principle_viz.core.aggregation import (
    AggregationError,
)
from principle_viz.core.line import Line
from principle_viz.plot.aggregation._figure import AggregationFigure
from principle_viz.plot.label import Label
from principle_viz.visuals.aggregation import (
    aggregation_panel,
    named_path_layers,
    quantity_guide_layers,
)
from principle_viz.visuals.theme import PlotTheme

MARGIN = 1.15
"""Room past the largest quantity and price, for arrows and curve names."""

HOLE = 0.035
"""Half-gap, as a share of the price axis, where a guide passes a step endpoint."""

DEMAND_ROLE = "principle.market.demand"
SUPPLY_ROLE = "principle.market.supply"


@dataclass(frozen=True)
class _Panel:
    panel_id: str
    title: str
    quantity: float
    quantity_label: str
    x_max: float
    draw: Callable[[Canvas], tuple[Layer, ...]]
    holes: tuple[tuple[float, float], ...] = ()


def _check(individuals: Mapping[str, object]) -> None:
    if not individuals:
        raise AggregationError("An aggregation figure needs at least one individual.")


def _theme(theme: PlotTheme | None, palette: str | None) -> PlotTheme:
    from principle_viz.config import default_theme  # avoids an import cycle

    return theme or default_theme(palette)


def _sub(symbol: str, name: str) -> str:
    """LaTeX subscript, braced when the name is longer than one character."""
    return f"{symbol}_{name}" if len(name) == 1 else f"{symbol}_{{{name}}}"


def _sum_label(names: list[str]) -> str:
    return "$" + " + ".join(_sub("Q", name) for name in names) + " = Q$"


def _build(
    panels: list[_Panel],
    *,
    y_max: float,
    price: float,
    price_label: str,
    theme: PlotTheme,
    point: bool,
    link_price: bool = False,
    labels: Mapping[str, Label] | None = None,
    visibility: Mapping[str, bool] | None = None,
) -> AggregationFigure:
    """Draw the panels; ``link_price`` runs the price guide across every panel
    and the gaps between them, marking the price on the first panel only."""
    canvases: list[Canvas] = []
    for index, panel in enumerate(panels):
        canvas = aggregation_panel(
            title=panel.title,
            x_max=panel.x_max,
            y_max=y_max,
            theme=theme,
            labels=labels,
            visibility=visibility,
        )
        canvas.extend(panel.draw(canvas))
        canvas.extend(
            quantity_guide_layers(
                panel_id=panel.panel_id,
                price=price,
                quantity=panel.quantity,
                price_label=price_label,
                quantity_label=panel.quantity_label,
                point=point,
                holes=panel.holes,
                hole=HOLE * y_max,
                price_mark=index == 0 or not link_price,
                price_until=panel.x_max if link_price else None,
            )
        )
        canvases.append(canvas)
    links = (
        tuple(
            GridLink(
                index,
                (left.x_max, price),
                index + 1,
                (0.0, price),
                role="principle.market.guide",
                stroke=Stroke(width=1.0, dash=DashStyle.DASHED),
            )
            for index, (left, _) in enumerate(pairwise(panels))
        )
        if link_price
        else ()
    )
    return AggregationFigure(tuple(canvases), links)


def _line_panels(
    individuals: Mapping[str, Line],
    market_points: tuple[tuple[float, float], ...],
    *,
    ends: Mapping[str, tuple[tuple[float, float], tuple[float, float]]],
    price: float,
    symbol: str,
    role: str,
) -> list[_Panel]:
    names = list(individuals)
    panels: list[_Panel] = []
    for name, line in individuals.items():
        start, end = ends[name]
        panels.append(
            _Panel(
                panel_id=name,
                title=f"Individual {name}",
                quantity=max(0.0, line.q_at(price)),
                quantity_label=f"${_sub('Q', name)}$",
                x_max=end[0] * MARGIN,
                draw=lambda canvas, n=name, s=start, e=end: named_path_layers(
                    canvas, (s, e), panel_id=n, role=role, label=f"${_sub(symbol, n)}$"
                ),
            )
        )
    market_q = sum(panel.quantity for panel in panels)
    active_names = [
        name for name, panel in zip(names, panels, strict=True) if panel.quantity > 0
    ]
    panels.append(
        _Panel(
            panel_id="market",
            title="Market",
            quantity=market_q,
            quantity_label=_sum_label(active_names),
            x_max=market_points[-1][0] * MARGIN,
            draw=lambda canvas: named_path_layers(
                canvas,
                market_points,
                panel_id="market",
                role=role,
                label=f"${symbol}$",
            ),
        )
    )
    return panels
