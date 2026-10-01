"""MosaicKit layers for labor and loanable-funds diagrams."""

from __future__ import annotations

from mosaickit import ArrowLayer, Layer, PathLayer, TextLayer

from principle_viz.core.factor_markets import LoanableFundsResult, MinimumWageResult
from principle_viz.visuals.curves import curve_layer
from principle_viz.visuals.equilibrium import equilibrium_layers, movement_layers


def minimum_wage_layers(
    result: MinimumWageResult, *, x_max: float
) -> tuple[Layer, ...]:
    layers: list[Layer] = [
        PathLayer(
            ((0, result.minimum_wage), (x_max, result.minimum_wage)),
            id="labor.minimum_wage",
            role="principle.policy.control",
            legend="Minimum wage",
            z_index=3,
        ),
        TextLayer(
            (0.02 * x_max, result.minimum_wage),
            f"Minimum wage = {result.minimum_wage:g}",
            id="labor.minimum_wage.label",
            role="principle.policy.control",
            offset=(0, 8),
            anchor="left",
            z_index=4,
        ),
        *equilibrium_layers(
            result.equilibrium,
            layer_id="labor.equilibrium",
            label=r"$L^*$",
        ),
    ]
    if result.is_binding and result.unemployment > 0:
        midpoint = 0.5 * (result.labor_demanded + result.labor_supplied)
        layers.extend(
            (
                ArrowLayer(
                    (result.labor_demanded, result.minimum_wage),
                    (result.labor_supplied, result.minimum_wage),
                    id="labor.unemployment",
                    role="principle.policy.control",
                    z_index=5,
                ),
                TextLayer(
                    (midpoint, result.minimum_wage),
                    f"Unemployment = {result.unemployment:g}",
                    id="labor.unemployment.label",
                    role="principle.policy.control",
                    offset=(0, 10),
                    anchor="bottom",
                    z_index=6,
                ),
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
                label="Savings (shifted)",
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
                label="Investment + borrowing",
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
