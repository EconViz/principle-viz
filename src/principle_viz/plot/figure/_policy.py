"""Policy, welfare and metrics methods of the market figure."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from principle_viz.core.controls import PriceControlResult
from principle_viz.core.factor_markets import LoanableFundsResult, MinimumWageResult
from principle_viz.plot.figure._wedges import _WedgeMixin
from principle_viz.policy.common_resources import CommonResourceResult
from principle_viz.policy.externality import ExternalityResult
from principle_viz.policy.trade import TradeComparisonResult
from principle_viz.visuals import (
    common_resource_layers,
    externality_layers,
    loanable_funds_layers,
    metrics_layer,
    minimum_wage_layers,
    price_control_layers,
    trade_layers,
    welfare_layers,
    welfare_overlay_layers,
)
from principle_viz.visuals.policy import GapBrace
from principle_viz.welfare.surplus import MarketOutcome, SurplusResult

if TYPE_CHECKING:
    from principle_viz.plot.figure import MarketFigure


class _PolicyMixin(_WedgeMixin):
    """Policy, welfare and metrics methods of the market figure."""

    def add_price_control(
        self, result: PriceControlResult, *, gap_brace: GapBrace = "line"
    ) -> MarketFigure:
        return self.add_layers(
            price_control_layers(result, x_max=self.x_max, gap_brace=gap_brace)
        )

    def add_minimum_wage(
        self, result: MinimumWageResult, *, gap_brace: GapBrace = "line"
    ) -> MarketFigure:
        return self.add_layers(
            minimum_wage_layers(result, x_max=self.x_max, gap_brace=gap_brace)
        )

    def add_loanable_funds(self, result: LoanableFundsResult) -> MarketFigure:
        return self._add_named_curves(loanable_funds_layers(result, q_max=self.x_max))

    def add_externality(self, result: ExternalityResult) -> MarketFigure:
        return self._add_named_curves(externality_layers(result, q_max=self.x_max))

    def add_common_resource(self, result: CommonResourceResult) -> MarketFigure:
        return self._add_named_curves(common_resource_layers(result, q_max=self.x_max))

    def add_trade(self, result: TradeComparisonResult) -> MarketFigure:
        return self._add_named_curves(trade_layers(result, x_max=self.x_max))

    def add_welfare(
        self,
        surplus: SurplusResult,
        *,
        labels: bool = True,
        regions: Iterable[str] | None = None,
    ) -> MarketFigure:
        """Shade the welfare regions and, unless ``labels`` is off, name each one.

        ``regions`` limits the shading to some of ``"cs"``, ``"ps"``,
        ``"tax_revenue"`` and ``"dwl"``.
        """
        return self.add_layers(welfare_layers(surplus, labels=labels, regions=regions))

    def add_welfare_transition(
        self,
        *,
        baseline_outcome: MarketOutcome,
        policy_outcome: MarketOutcome,
        surplus: SurplusResult,
    ) -> MarketFigure:
        self.add_welfare(surplus)
        return self.add_layers(
            welfare_overlay_layers(
                baseline_outcome=baseline_outcome,
                policy_outcome=policy_outcome,
                surplus=surplus,
            )
        )

    def add_metrics(
        self,
        metrics: dict[str, object],
        *,
        title: str | None = None,
        location: str = "upper right",
    ) -> MarketFigure:
        metric_count = sum(
            layer.id.startswith("market.metrics.") for layer in self.scene.layers
        )
        return self.add_layer(
            metrics_layer(
                metrics,
                x_max=self.x_max,
                y_max=self.y_max,
                layer_id=f"market.metrics.{metric_count}",
                title=title,
                location=location,
            )
        )
