"""Individual | individual | market figures for horizontal summation."""

from principle_viz.plot.aggregation._continuous import (
    demand_aggregation_figure,
    supply_aggregation_figure,
)
from principle_viz.plot.aggregation._discrete import (
    discrete_demand_aggregation_figure,
    discrete_supply_aggregation_figure,
)
from principle_viz.plot.aggregation._figure import AggregationFigure
from principle_viz.plot.aggregation._panels import (
    DEMAND_ROLE as DEMAND_ROLE,
)
from principle_viz.plot.aggregation._panels import (
    HOLE as HOLE,
)
from principle_viz.plot.aggregation._panels import (
    MARGIN as MARGIN,
)
from principle_viz.plot.aggregation._panels import (
    SUPPLY_ROLE as SUPPLY_ROLE,
)

__all__ = [
    "AggregationFigure",
    "demand_aggregation_figure",
    "discrete_demand_aggregation_figure",
    "discrete_supply_aggregation_figure",
    "supply_aggregation_figure",
]
