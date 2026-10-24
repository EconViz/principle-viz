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
scenario = TaxScenario(
    tax_type=TaxType.AD_VALOREM_TAX, amount=0.35, tax_on=TaxOn.CONSUMER
)

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

## Labels

Every built-in label has a stable id (`figure.label_ids`). A `Label` renames, hides or moves one:

```python
from principle_viz import Label, MarketFigure

figure = MarketFigure(labels={"market.equilibrium": Label(top="4pt")})
figure.configure_label("market.supply", Label(right="8pt"))
figure.configure_label("market.demand", text="$D_0$", left="0.5em")
```

`top`, `bottom`, `left` and `right` move the label that far after it has been placed, so
principle-viz still picks the spot and you only fine-tune it. A length is a number of points or a
string with a unit: `"10pt"`, `"0.5em"` (the label's font size) or `"2mm"`; `top` and `bottom`
combine, as do `right` and `left`. `Label(offset=(dx, dy))` still places a label at an exact
offset in points instead of automatically; a nudge then moves it from there. Axis labels (the axis
names, the origin and the marks on the axes) do not take nudges.

To move a whole group of labels at once, set a default in `econ-viz.toml` (see Settings File).

## Settings File

principle-viz reads `econ-viz.toml`, the settings file every EconViz package shares; mosaickit
reads and checks it. The top level sets the starting colour model (`base`), the fonts and the axis
and label colours; principle-viz's own settings live in the `[principle]` table, and the tables of
other packages, such as `[utility]`, are skipped.

```toml
base = "default"     # a shared theme: manual, default, colorblind, monochrome, nord,
                     # paper or presentation

[font]
text = "serif"
math = "fonts/texgyrepagella-math.otf"

[fonts]
serif = ["fonts/NotoSerifTC-Regular.otf", "fonts/NotoSerifTC-Bold.otf"]

[color]
axis = "#1a1a1a"
label = "#1a1a1a"

[principle]
palette = "manual"   # colour model for principle-viz only; wins over base
language = "zh-TW"   # language of built-in figure text

[principle.color]    # any colour-model role, without "_color"
demand = "#8c8c8c"
supply = "#1a1a1a"

[principle.stroke]   # line widths in points
demand = 3.5

[principle.marker]
equilibrium = 6.5    # equilibrium dot diameter in points

[principle.label.point]   # default move for a group of labels
top = "2pt"               # also bottom, left, right: pt, mm, cm or in (no em); unset = no move
```

```python
from principle_viz import Config

Config.load("econ-viz.toml").use()  # figures made without theme= use it
```

### Label nudges

`[principle.label.<group>]` moves every label of a group by default. Each group takes `top`,
`bottom`, `left` and `right`, lengths as in `Label` (a number of points, or `"2pt"`, `"1mm"`,
`"0.1cm"`, `"0.05in"`; `em` is not accepted because the file has no font size). `top` and `bottom`
combine, as do `right` and `left`. The groups follow what a label names:

| group | labels |
|---|---|
| `point` | equilibrium points (`e_0`, `e^*`, `e_1`, `e_t`, `L^*`, the discrete `Q^* = ..., p^* = ...`) and the points of a PPF |
| `curve` | curves named at their end: `D`, `S`, `D_1`, `S + t`, `MSB`, `MSC`, `MC`, `\Sigma MB`, `PPF`, `PPF_0`, `PPF_1` |
| `region` | names inside filled regions, callouts with a leader line included: consumer and producer surplus, deadweight loss, tax revenue, subsidy cost, tariff revenue |
| `mark` | price lines and policy marks: `p_c`, `p_f`, `w_min`, `p_w`, `p_w + t`, the `t = ...`, `s = ...` and `f = ...` wedges |
| `annotation` | other text: brace labels (Shortage, Tax, Subsidy, Imports, Unemployment), price intervals, metrics, elasticity zone names |

Axis labels (axis names, origin, the `Q_0`, `p_1` marks and their notes) belong to no group. A
callout's leader line keeps pointing at the moved label.

A label given its own `top`, `bottom`, `left` or `right` (`Label(top=...)`, `labels=`,
`configure_label`) is moved by those values and **not** by its group's default: the per-label
nudge replaces the default, they do not add up. A `Label` that only renames, hides or sets an
`offset` keeps the default nudge. Without `[principle.label.*]` settings figures are drawn exactly
as before.

### Moving one label of one figure

`[figure.<stem>.label."<layer id>"]` moves a single label of the figure saved as `<stem>.png`
(or `.svg`, `.pdf`). It sits at the top level of `econ-viz.toml`, next to `[principle]`, and
mosaickit reads and applies it, so nothing in your Python changes:

```toml
[figure.tax_welfare.label."market.welfare.dwl.label"]
top = "12pt"
```

`MarketFigure.save()`, the canvases of the `principle_viz.visuals` helpers (`.save()`) and
`AggregationFigure.save()` apply it once a config read from the file is active (`Config.load(...).use()`).
The stem is the one of the path given to `save()`. The override **replaces** the label's nudge,
whether it came from `Label(top=...)` or from `[principle.label.<group>]`, so `top = "12pt"` means 12 pt
up, not 12 pt on top of the group default; an empty table cancels the nudge. A callout's leader
follows. `MarketFigure.save(path, dpi=...)` behaves the same. Ids that no label has are ignored.

The key is the layer id of the label: the entries of `MarketFigure.label_ids` (for example
`market.demand.label`, `market.welfare.dwl.label`, `market.equilibrium.label`,
`market.control.gap`), which is also the `id` of the element in the saved SVG; a brace's label is
`<brace id>.label`. Axis marks (`Q_0`, `p_c`, ...) cannot be moved this way, and the label of a
brace drawn in the axis gutter (side `outside`, such as the tax and subsidy wedge) accepts the
key but mosaickit does not move it yet. Needs `mosaickit>=1.0.0rc7`.

### Themes

The colour models are mosaickit's shared themes (`mosaickit.themes`), so `base = "nord"` means the
same look in every EconViz package. A theme gives a colour to each role, and
`principle_viz.visuals.roles` says which role each figure element takes:

| role | elements |
|---|---|
| ink | axis, label, baseline, arrow |
| primary | demand |
| secondary | supply |
| tertiary | shifted |
| intervention | tax, control |
| fill.light / fill.mid / fill.dark / fill.faint | cs / ps / dwl / tax_revenue |

The theme's line and marker scales multiply principle-viz's own line widths and equilibrium dot
(`presentation` draws them 1.5 and 1.3 times as large). `PlotTheme.from_palette(name)`,
`get_color_model(name)` and `palette=name` take the same names; `[principle.color]` still sets one
element.

A `theme=` or `palette=` passed to a figure still wins. Relative paths are resolved against the
file's directory. A mistake raises `mosaickit.ConfigurationError` naming the file and the table,
e.g. `econ-viz.toml: [principle.color] unknown key 'demnad'; did you mean 'demand'?`.

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
