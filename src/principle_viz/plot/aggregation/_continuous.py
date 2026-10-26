"""Aggregation figures for straight-line demands and supplies."""

from __future__ import annotations

from collections.abc import Mapping

from principle_viz.core.aggregation import (
    AggregationError,
    market_demand,
    market_supply,
)
from principle_viz.core.line import Line
from principle_viz.plot.aggregation._figure import AggregationFigure
from principle_viz.plot.aggregation._panels import (
    DEMAND_ROLE,
    MARGIN,
    SUPPLY_ROLE,
    _build,
    _check,
    _line_panels,
    _theme,
)
from principle_viz.plot.label import Label
from principle_viz.visuals.theme import PlotTheme


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
