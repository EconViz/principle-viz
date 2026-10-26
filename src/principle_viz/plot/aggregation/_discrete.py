"""Aggregation figures for unit demand and supply schedules."""

from __future__ import annotations

from collections.abc import Mapping

from principle_viz.core.aggregation import (
    AggregationError,
)
from principle_viz.core.discrete import DiscreteDemand, DiscreteSupply
from principle_viz.plot.aggregation._figure import AggregationFigure
from principle_viz.plot.aggregation._panels import (
    DEMAND_ROLE,
    MARGIN,
    SUPPLY_ROLE,
    _build,
    _check,
    _Panel,
    _sub,
    _sum_label,
    _theme,
)
from principle_viz.plot.label import Label
from principle_viz.visuals.aggregation import (
    named_schedule_layers,
)
from principle_viz.visuals.theme import PlotTheme


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
