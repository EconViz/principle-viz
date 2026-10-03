<p align="center">
  <img src="https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/banner.svg" alt="principle-viz" width="480">
</p>

<p align="center">
  <a href="https://github.com/EconViz/principle-viz/actions/workflows/publish.yml"><img alt="CI / Publish" src="https://img.shields.io/github/actions/workflow/status/EconViz/principle-viz/publish.yml?branch=main&style=flat-square&color=181818&labelColor=f3f3f3&label=CI%20%2F%20Publish"></a>
  <a href="https://pypi.org/project/principle-viz/"><img alt="PyPI" src="https://img.shields.io/pypi/v/principle-viz?style=flat-square&color=181818&labelColor=f3f3f3"></a>
  <a href="https://pypi.org/project/principle-viz/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/principle-viz?style=flat-square&color=181818&labelColor=f3f3f3"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License" src="https://img.shields.io/badge/License-MIT-181818?style=flat-square&color=181818&labelColor=f3f3f3"></a>
  <a href="https://github.com/EconViz/principle-viz/tree/docs"><img alt="Docs Branch" src="https://img.shields.io/badge/docs-branch-181818?style=flat-square&color=181818&labelColor=f3f3f3"></a>
</p>

`principle-viz` is a Python package for Principles of Economics market analysis and diagrams.
It focuses on **linear demand/supply** models with clean module boundaries across solver logic, policy layers, welfare decomposition, and plotting.

## Features

- Solve market equilibrium from linear demand and supply, or from discrete unit schedules
- Comparative statics: shifts of demand or supply, with the move from the old equilibrium to the new one
- Taxes (fixed, per-unit, ad valorem; legal incidence on buyers or sellers) and subsidies
- Price ceilings, price floors and the minimum wage, with the shortage, surplus or unemployment braced on the policy line
- Welfare decomposition: consumer and producer surplus, tax revenue, deadweight loss
- International trade (free trade, tariffs, quotas), externalities, common resources, public goods, loanable funds, the PPF and elasticity
- Market demand and supply as the horizontal sum of individual curves or schedules
- Textbook-style figures built on [MosaicKit](https://github.com/EconViz/mosaickit): square plots, curves named directly instead of a legend, LaTeX labels, values marked on the axes, and labels placed so they cover nothing
- CLI workflows with JSON output

## Installation

```bash
pip install principle-viz
```

For development:

```bash
git clone https://github.com/EconViz/principle-viz.git
cd principle-viz
uv sync
```

## Quick Start

```python
from principle_viz.core.line import Line
from principle_viz.core.equilibrium import solve_equilibrium
from principle_viz.plot.figure import MarketFigure

demand = Line.from_inverse(10.0, -1.0)
supply = Line.from_inverse(2.0, 1.0)
eq = solve_equilibrium(demand, supply)

fig = MarketFigure(x_max=12, y_max=12, title="Basic Equilibrium")
fig.add_curves(demand, supply, q_max=10)
fig.add_equilibrium(eq)
fig.finalize()
fig.save("basic_equilibrium.png")
fig.close()
```

## Tax Example (Consumer vs Producer Incidence)

```python
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure
from principle_viz.policy.tax import TaxOn, TaxScenario, TaxType

demand = Line.from_inverse(10.0, -1.0)
supply = Line.from_inverse(0.0, 1.0)
scenario = TaxScenario(tax_type=TaxType.AD_VALOREM_TAX, amount=0.35, tax_on=TaxOn.CONSUMER)

fig = MarketFigure(x_max=12, y_max=12, title="Ad Valorem Tax")
fig.add_curves(demand, supply, q_max=10)
fig.add_tax_transform(demand, supply, scenario, q_max=10)
fig.finalize()
fig.save("tax_ad_valorem_consumer.png")
fig.close()
```

## Price Controls

```python
from principle_viz.core.controls import (
    PriceControlScenario,
    PriceControlType,
    evaluate_price_control,
)
from principle_viz.core.line import Line
from principle_viz.plot.figure import MarketFigure

demand = Line.from_inverse(10.0, -1.0)
supply = Line.from_inverse(2.0, 1.0)
ceiling = evaluate_price_control(
    demand, supply, PriceControlScenario(PriceControlType.CEILING, 4.0)
)

fig = MarketFigure(x_max=12, y_max=12, title="Binding Price Ceiling")
fig.add_curves(demand, supply, q_max=10)
fig.add_price_control(ceiling)  # "Shortage" braced below the ceiling line
fig.finalize()
fig.save("price_ceiling.png")
fig.close()
```

`add_price_control(..., gap_brace="axis")` braces the gap under the quantity axis instead; `add_minimum_wage()` draws the labor-market version.

## Market Demand and Supply from Individuals

Individual curves sum horizontally into the market curve. Each buyer buys nothing above their choke price and each seller sells nothing below their minimum price, so the market curve is piecewise linear with a kink at each of those prices.

```python
from principle_viz import (
    DiscreteDemand,
    demand_aggregation_figure,
    discrete_demand_aggregation_figure,
    market_demand,
    market_supply,
    solve_piecewise_equilibrium,
)
from principle_viz.core.line import Line

a = Line.from_inverse(10, -2)  # p = 10 - 2Q
b = Line.from_inverse(6, -0.5)  # p = 6 - 0.5Q
demand = market_demand((a, b))
demand.points  # ((0, 10), (2, 6), (17, 0)), kink at B's choke price
demand.q_at(4)  # 7 = Q_A + Q_B

supply = market_supply((Line.from_inverse(2, 1), Line.from_inverse(5, 0.5)), p_max=10)
solve_piecewise_equilibrium(demand, supply)  # exact on each segment

# Individual A | individual B | market, with guides at p_1 showing Q_A + Q_B = Q.
# link_price=True runs the p_1 line across all three panels.
demand_aggregation_figure({"A": a, "B": b}, price=4, link_price=True).save(
    "market_demand.png"
)

# Discrete: reservation prices combine into one market step schedule.
DiscreteDemand.combine(DiscreteDemand((10, 7, 4)), DiscreteDemand((8, 5, 2)))
discrete_demand_aggregation_figure(
    {"A": DiscreteDemand((10, 7, 4)), "B": DiscreteDemand((8, 5, 2))}, price=6
).save("discrete_market_demand.png")
```

`supply_aggregation_figure` and `discrete_supply_aggregation_figure` draw the supply side. Examples: `examples/scripts/aggregation_*.py`, output under `examples/output/aggregation/`.

## CLI

```bash
principle-viz equilibrium \
  --demand-intercept 10 --demand-slope -1 \
  --supply-intercept 2 --supply-slope 1

principle-viz tax \
  --demand-intercept 10 --demand-slope -1 \
  --supply-intercept 2 --supply-slope 1 \
  --tax-type per_unit --amount 1 --tax-on producer
```

## Examples

Run all examples:

```bash
uv run python examples/scripts/run_all.py
```

Generated images are grouped by topic under `examples/output/`: `equilibrium/`, `discrete/`, `aggregation/`, `taxation/`, `subsidy/`, `price_controls/`, `welfare/`, `trade/`, `market_failures/`, `factor_capital_markets/`, `elasticity/` and `ppf/`.

### Example Gallery

| | |
|---|---|
| ![Increase in Demand](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/comparative_statics_demand_increase.png) | ![Binding Price Ceiling](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/price_controls.png) |
| ![Welfare Change from a Tax](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/welfare_tax.png) | ![Import Tariff](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/import_tariff.png) |
| ![Negative Externality](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/negative_externality.png) | ![Discrete Demand and Supply](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/discrete_market.png) |

![Market Demand](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/market_demand_linked.png)

## Development

```bash
uv run ruff check src tests examples/scripts
uv run pytest -q
uv build
```

## PyPI Publishing

This repository is configured to publish from GitHub Actions using Trusted Publishing.

- Workflow: `.github/workflows/publish.yml`
- Trigger: push tag `v*` (for example `v0.1.0`)
- Publisher: `pypa/gh-action-pypi-publish@release/v1` with `id-token: write`

To release: bump the version in `pyproject.toml` and the CHANGELOG heading on a `release/vX.Y.Z` branch, merge it, then create the GitHub release `vX.Y.Z`; the tag push builds and publishes to PyPI.

## Brand Assets

Brand SVG assets and banner are tracked in the `docs` branch so raw URLs stay stable:

- Banner: `docs/assets/banner.svg`
- Logo: `docs/assets/logo.svg`

## Documentation

- Visual language (in Chinese): [`docs/visual-language.md`](https://github.com/EconViz/principle-viz/blob/main/docs/visual-language.md)
- Contribution guide: [`CONTRIBUTING.md`](https://github.com/EconViz/principle-viz/blob/main/CONTRIBUTING.md)
- Changelog: [`CHANGELOG.md`](https://github.com/EconViz/principle-viz/blob/main/CHANGELOG.md)

## License

MIT
