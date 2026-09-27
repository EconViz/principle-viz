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

- Solve market equilibrium from two linear equations
- Comparative statics with direction metadata
- Tax analysis: fixed, per-unit, ad valorem, and legal incidence side
- Price controls: ceiling/floor with shortage/surplus
- Welfare decomposition: CS, PS, tax revenue, TS, DWL
- Renderer-friendly polygon outputs and labeled welfare regions
- CLI workflows with JSON output
- Example figures generated in monochrome style for teaching slides

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

fig = MarketFigure(x_max=12, y_max=12, title="Basic Equilibrium", palette="monochrome")
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
scenario = TaxScenario(tax_type=TaxType.AD_VALOREM_TAX, amount=0.2, tax_on=TaxOn.CONSUMER)

fig = MarketFigure(x_max=11, y_max=11, title="Ad Valorem Tax", palette="monochrome")
fig.add_curves(demand, supply, q_max=10)
fig.add_tax_transform(demand, supply, scenario, q_max=10)
fig.finalize(legend=True)
fig.save("tax_ad_valorem_consumer.png")
fig.close()
```

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
uv run python examples/scipts/run_all.py
```

Generated images are grouped by topic under `examples/output/`:

- `equilibrium/`
- `taxation/`
- `price_controls/`
- `welfare/`
- `elasticity/`

### Example Gallery

![Basic Equilibrium](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/basic_equilibrium.png)

![Comparative Statics](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/comparative_statics.png)

![Tax (Ad Valorem, Consumer)](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/tax_ad_valorem_consumer.png)

![Price Controls and Welfare](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/price_controls_welfare.png)

![Tax Welfare Decomposition](https://raw.githubusercontent.com/EconViz/principle-viz/docs/docs/assets/examples/welfare_tax.png)

## Development

```bash
uv run ruff check src tests examples/scipts
uv run pytest -q
uv build
```

## PyPI Publishing

This repository is configured to publish from GitHub Actions using Trusted Publishing.

- Workflow: `.github/workflows/publish.yml`
- Trigger: push tag `v*` (for example `v0.1.0`)
- Publisher: `pypa/gh-action-pypi-publish@release/v1` with `id-token: write`

Release helper script (modeled after `econ-viz`):

```bash
scripts/release.sh prepare 0.1.0
scripts/release.sh finalize 0.1.0
```

## Brand Assets

Brand SVG assets and banner are tracked in the `docs` branch so raw URLs stay stable:

- Banner: `docs/assets/banner.svg`
- Logo: `docs/assets/logo.svg`

## Documentation

- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Contribution guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md)

## License

MIT
