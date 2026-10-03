"""MosaicKit layers for labor and loanable-funds diagrams."""

from __future__ import annotations

from mosaickit import AxisMarkLayer, Layer, PathLayer, PointLabelLayer

from principle_viz.core.factor_markets import LoanableFundsResult, MinimumWageResult
from principle_viz.visuals.curves import curve_layer
from principle_viz.visuals.equilibrium import equilibrium_layers, movement_layers
from principle_viz.visuals.policy import GapBrace, gap_brace_layer


def minimum_wage_layers(
    result: MinimumWageResult, *, x_max: float, gap_brace: GapBrace = "line"
) -> tuple[Layer, ...]:
    """The wage floor, named directly, with ``w_min`` on the wage axis. A binding
    floor also marks ``L_d`` and ``L_s`` with guides and braces the unemployment
    between them above the floor (``gap_brace="axis"`` braces it on the labor axis).
    """
    role = "principle.policy.control"
    wage = result.minimum_wage
    layers: list[Layer] = [
        PathLayer(
            ((0, wage), (x_max, wage)),
            id="labor.minimum_wage",
            role=role,
            legend=r"$w_{\min}$",
            z_index=3,
        ),
        PointLabelLayer(
            (x_max, wage),
            r"$w_{\min}$",
            id="labor.minimum_wage.label",
            role=role,
            z_index=4,
        ),
        AxisMarkLayer("y", wage, r"w_{\min}", math=True, id="labor.mark.w_min"),
        *equilibrium_layers(
            result.equilibrium,
            layer_id="labor.equilibrium",
            label=r"$L^*$",
        ),
    ]
    if result.is_binding and result.unemployment > 0:
        for symbol, quantity in (
            ("L_d", result.labor_demanded),
            ("L_s", result.labor_supplied),
        ):
            key = symbol.lower()
            layers.extend(
                (
                    PathLayer(
                        ((quantity, 0.0), (quantity, wage)),
                        id=f"labor.guide.{key}",
                        role="principle.market.guide",
                        z_index=2,
                    ),
                    AxisMarkLayer(
                        "x", quantity, symbol, math=True, id=f"labor.mark.{key}"
                    ),
                )
            )
        layers.append(
            gap_brace_layer(
                result.labor_demanded,
                result.labor_supplied,
                wage,
                "Unemployment",
                side="above",
                layer_id="labor.unemployment",
                where=gap_brace,
            )
        )
    return tuple(layers)


def loanable_funds_layers(
    result: LoanableFundsResult, *, q_max: float
) -> tuple[Layer, ...]:
    layers: list[Layer] = []
    if result.shifted_savings.as_tuple() != result.savings_supply.as_tuple():
        layers.append(
            curve_layer(
                result.shifted_savings,
                q_min=0,
                q_max=q_max,
                layer_id="loanable.savings.shifted",
                role="principle.market.supply.shifted",
                label="$S_1$",
            )
        )
    if (
        result.shifted_investment_demand.as_tuple()
        != result.investment_demand.as_tuple()
    ):
        layers.append(
            curve_layer(
                result.shifted_investment_demand,
                q_min=0,
                q_max=q_max,
                layer_id="loanable.investment.shifted",
                role="principle.market.demand.shifted",
                label="$D_1$",
            )
        )
    layers.extend(
        equilibrium_layers(
            result.baseline_equilibrium,
            layer_id="loanable.equilibrium.baseline",
            label=r"$e_0$",
        )
    )
    layers.extend(
        equilibrium_layers(
            result.shifted_equilibrium,
            layer_id="loanable.equilibrium.shifted",
            role="principle.market.equilibrium.shifted",
            label=r"$e_1$",
        )
    )
    layers.extend(
        movement_layers(result.baseline_equilibrium, result.shifted_equilibrium)
    )
    return tuple(layers)


__all__ = ["loanable_funds_layers", "minimum_wage_layers"]
