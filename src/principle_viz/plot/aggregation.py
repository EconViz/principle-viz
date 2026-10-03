"""Individual | individual | market figures for horizontal summation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

from mosaickit import Canvas, CanvasGrid, DashStyle, GridLink, Layer, Stroke

from principle_viz.core.aggregation import (
    AggregationError,
    market_demand,
    market_supply,
)
from principle_viz.core.discrete import DiscreteDemand, DiscreteSupply
from principle_viz.core.line import Line
from principle_viz.plot.label import Label
from principle_viz.visuals.aggregation import (
    aggregation_panel,
    named_path_layers,
    named_schedule_layers,
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
class AggregationFigure:
    """Side-by-side panels: one per individual, then the market."""

    panels: tuple[Canvas, ...]
    links: tuple[GridLink, ...] = ()

    @property
    def grid(self) -> CanvasGrid:
        return CanvasGrid(self.panels, rows=1, links=self.links)

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.grid.save(target)
        return target

    @property
    def layer_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(id_ for panel in self.panels for id_ in panel.layer_ids))

    @property
    def label_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(id_ for panel in self.panels for id_ in panel.label_ids))

    def hide(self, *layer_ids: str) -> AggregationFigure:
        return self._set_visibility(layer_ids, visible=False)

    def show(self, *layer_ids: str) -> AggregationFigure:
        return self._set_visibility(layer_ids, visible=True)

    def _set_visibility(
        self,
        layer_ids: tuple[str, ...],
        *,
        visible: bool,
    ) -> AggregationFigure:
        for layer_id in layer_ids:
            matched = False
            for panel in self.panels:
                if layer_id in panel.layer_ids:
                    panel.configure_layer(layer_id, visible=visible)
                    matched = True
            if not matched:
                raise KeyError(f"Unknown aggregation layer {layer_id!r}")
        return self

    def configure_label(
        self,
        layer_id: str,
        label: Label | None = None,
        *,
        text: str | None = None,
        visible: bool | None = None,
        offset: tuple[float, float] | None = None,
    ) -> AggregationFigure:
        matched = False
        for panel in self.panels:
            if layer_id in panel.label_ids or f"{layer_id}.label" in panel.label_ids:
                panel.configure_label(
                    layer_id,
                    label,
                    text=text,
                    visible=visible,
                    offset=offset,
                )
                matched = True
        if not matched:
            raise KeyError(f"Unknown aggregation label {layer_id!r}")
        return self


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
    return theme or PlotTheme.from_palette(palette or "default")


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
        name
        for name, panel in zip(names, panels, strict=True)
        if panel.quantity > 0
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


def demand_aggregation_figure(
    individuals: Mapping[str, Line],
    *,
    price: float,
    price_label: str = "$p_1$",
    theme: PlotTheme | None = None,
    palette: str | None = None,
    link_price: bool = False,
    labels: Mapping[str, Label] | None = None,
    visibility: Mapping[str, bool] | None = None,
) -> AggregationFigure:
    """Individual demands, their horizontal sum, and the quantities at ``price``.

    ``link_price=True`` runs the price line across every panel and the gaps
    between them, as one line, and marks the price on the first panel only.
    """
    _check(individuals)
    market = market_demand(individuals.values())
    top = market.price_range[1]
    if not 0 < price < top:
        raise AggregationError(
            f"price must lie strictly between 0 and the highest choke price ({top:g})."
        )
    ends = {
        name: ((0.0, line.p_intercept()), (line.q_intercept(), 0.0))
        for name, line in individuals.items()
    }
    panels = _line_panels(
        individuals,
        market.points,
        ends=ends,
        price=price,
        symbol="D",
        role=DEMAND_ROLE,
    )
    return _build(
        panels,
        y_max=top * MARGIN,
        price=price,
        price_label=price_label,
        theme=_theme(theme, palette),
        point=True,
        link_price=link_price,
        labels=labels,
        visibility=visibility,
    )


def supply_aggregation_figure(
    individuals: Mapping[str, Line],
    *,
    price: float,
    p_max: float,
    price_label: str = "$p_1$",
    theme: PlotTheme | None = None,
    palette: str | None = None,
    link_price: bool = False,
    labels: Mapping[str, Label] | None = None,
    visibility: Mapping[str, bool] | None = None,
) -> AggregationFigure:
    """Individual supplies up to ``p_max``, their sum, and quantities at ``price``.

    ``link_price=True`` runs the price line across every panel and the gaps
    between them, as one line, and marks the price on the first panel only.
    """
    _check(individuals)
    market = market_supply(individuals.values(), p_max=p_max)
    bottom = market.price_range[0]
    if not bottom < price <= p_max:
        raise AggregationError(
            f"price must lie above the lowest minimum price ({bottom:g}) "
            f"and at most p_max ({p_max:g})."
        )
    ends = {
        name: ((0.0, line.p_intercept()), (line.q_at(p_max), float(p_max)))
        for name, line in individuals.items()
    }
    panels = _line_panels(
        individuals,
        market.points,
        ends=ends,
        price=price,
        symbol="S",
        role=SUPPLY_ROLE,
    )
    return _build(
        panels,
        y_max=p_max * MARGIN,
        price=price,
        price_label=price_label,
        theme=_theme(theme, palette),
        point=True,
        link_price=link_price,
        labels=labels,
        visibility=visibility,
    )


def _discrete_figure(
    individuals: Mapping[str, DiscreteDemand | DiscreteSupply],
    market: DiscreteDemand | DiscreteSupply,
    *,
    price: float,
    price_label: str,
    symbol: str,
    role: str,
    theme: PlotTheme,
    link_price: bool,
    labels: Mapping[str, Label] | None,
    visibility: Mapping[str, bool] | None,
) -> AggregationFigure:
    if price <= 0:
        raise AggregationError("price must be positive.")
    color = theme.demand_color if role == DEMAND_ROLE else theme.supply_color
    names = list(individuals)
    schedules = [*individuals.items(), ("market", market)]
    panels: list[_Panel] = []
    for name, schedule in schedules:
        is_market = name == "market"
        label = f"${symbol}$" if is_market else f"${_sub(symbol, name)}$"
        quantity = schedule.quantity_at(price)
        # At Q sit the end of unit Q, the start of unit Q + 1 and the dashed
        # riser between them: the quantity guide skips that whole span.
        values = schedule.values
        x_max = schedule.unit_count * MARGIN + 0.6
        ends = [values[i] for i in (quantity - 1, quantity) if 0 <= i < len(values)]
        holes = ((min(ends), max(ends)),) if ends else ()
        panels.append(
            _Panel(
                panel_id=name,
                title="Market" if is_market else f"Individual {name}",
                quantity=float(quantity),
                holes=holes,
                quantity_label=_sum_label(names)
                if is_market
                else f"${_sub('Q', name)}$",
                x_max=x_max,
                draw=lambda canvas, n=name, s=schedule, lab=label: (
                    named_schedule_layers(
                        canvas, s, panel_id=n, role=role, color=color, label=lab
                    )
                ),
            )
        )
    return _build(
        panels,
        y_max=max(max(s.values) for _, s in schedules) * MARGIN,
        price=price,
        price_label=price_label,
        theme=theme,
        point=False,
        link_price=link_price,
        labels=labels,
        visibility=visibility,
    )


def discrete_demand_aggregation_figure(
    individuals: Mapping[str, DiscreteDemand],
    *,
    price: float,
    price_label: str = "$p_1$",
    theme: PlotTheme | None = None,
    palette: str | None = None,
    link_price: bool = False,
    labels: Mapping[str, Label] | None = None,
    visibility: Mapping[str, bool] | None = None,
) -> AggregationFigure:
    """Individual unit demands, the combined market schedule, and units at ``price``.

    ``link_price=True`` runs the price line across every panel and the gaps
    between them, as one line, and marks the price on the first panel only.
    """
    _check(individuals)
    return _discrete_figure(
        individuals,
        DiscreteDemand.combine(*individuals.values()),
        price=price,
        price_label=price_label,
        symbol="D",
        role=DEMAND_ROLE,
        theme=_theme(theme, palette),
        link_price=link_price,
        labels=labels,
        visibility=visibility,
    )


def discrete_supply_aggregation_figure(
    individuals: Mapping[str, DiscreteSupply],
    *,
    price: float,
    price_label: str = "$p_1$",
    theme: PlotTheme | None = None,
    palette: str | None = None,
    link_price: bool = False,
    labels: Mapping[str, Label] | None = None,
    visibility: Mapping[str, bool] | None = None,
) -> AggregationFigure:
    """Individual unit costs, the combined market schedule, and units at ``price``.

    ``link_price=True`` runs the price line across every panel and the gaps
    between them, as one line, and marks the price on the first panel only.
    """
    _check(individuals)
    return _discrete_figure(
        individuals,
        DiscreteSupply.combine(*individuals.values()),
        price=price,
        price_label=price_label,
        symbol="S",
        role=SUPPLY_ROLE,
        theme=_theme(theme, palette),
        link_price=link_price,
        labels=labels,
        visibility=visibility,
    )


__all__ = [
    "AggregationFigure",
    "demand_aggregation_figure",
    "discrete_demand_aggregation_figure",
    "discrete_supply_aggregation_figure",
    "supply_aggregation_figure",
]
