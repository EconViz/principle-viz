# CHANGELOG

All notable changes to this project are documented in this file.

## Unreleased

### Features

- `PlotTheme(font_family=...)` sets the default font for the complete figure.
  `font_families` maps semantic roles such as `title`, `axes`, or
  `principle.market.demand` to specific families for per-label typography.

## v0.10.0 (2026-10-03)

### Features

- Market curves from individual curves (#23). `market_demand()` and `market_supply(..., p_max=...)` sum linear individual curves horizontally into a new `PiecewiseLinear` curve (`q_at`, `p_at`, `kinks`, `domain`, `price_range`, `integrate_q`) with a kink at each individual's choke price or minimum price. `solve_piecewise_equilibrium()` solves the market exactly on each segment and `piecewise_surplus()` integrates consumer and producer surplus. Invalid input raises `AggregationError` or `PiecewiseLinearError` with the reason.
- `DiscreteDemand.combine()` / `DiscreteSupply.combine()` merge individual reservation prices or unit costs into one market schedule (ties kept as separate units), and `quantity_at(price)` counts the units bought or sold at a price; the existing discrete solver works on the combined schedules.
- `demand_aggregation_figure()`, `supply_aggregation_figure()`, `discrete_demand_aggregation_figure()` and `discrete_supply_aggregation_figure()` return an `AggregationFigure`: side-by-side `CanvasGrid` panels (one per individual, then the market) sharing the price axis, curves named directly (`$D_A$`, `$D_B$`, `$D$`; `$S_A$`, `$S_B$`, `$S$`), and dashed guides at a chosen price marked `$p_1$`, `$Q_A$`, `$Q_B$` and `$Q_A + Q_B = Q$`. Discrete panels draw steps with filled (included) and open (excluded) endpoints. New examples `aggregation_demand.py`, `aggregation_supply.py`, `aggregation_discrete_demand.py`, `aggregation_discrete_supply.py` write to `examples/output/aggregation/`.

### Changed

- Discrete step schedules draw open endpoints with an opaque white face (the step no longer shows through them) and a thin dashed riser, in the schedule's colour, from each open endpoint to the closed point that starts the next step. Points on an axis are drawn whole.
- `MarketFigure.add_discrete_curves()` accepts a demand schedule, a supply schedule, or both. New example `discrete_schedules.py` draws each alone.
- Aggregation figures take `link_price=True` to run the price line across every panel and the gaps between them (via MosaicKit `GridLink`), marking the price on the first panel only. In discrete panels the quantity guide no longer doubles the step's riser at `Q`. New example outputs `market_demand_linked.png` and `market_supply_linked.png`.
- Movement arrows (comparative statics, loanable funds, tax shifts and rotations) are thin (1.2 pt), black and dashed, and their labels are black.
- `add_comparative_statics()` redraws only the curve that moved. The example now draws four figures, one shift each (increase/decrease in demand/supply), with a larger shift.
- The elasticity example names each point without values and puts the perfectly elastic and perfectly inelastic points on the axes.
- Removed the DWL summary bar-chart example (`build_dwl_report()` is unchanged).

- Depend on `mosaickit>=0.5.1,<0.6.0`.
- `MarketFigure.finalize()` no longer adds a legend by default. Pass `finalize(legend=True)` to keep the previous behaviour.
- The `default` palette now takes its hues from MosaicKit's `DEFAULT_PALETTE`: demand blue, supply red, deadweight loss teal. Consumer and producer surplus reuse the demand and supply hues at 15% opacity, deadweight loss is 45%, and tax revenue is labelled rather than shaded. Supply and demand curves (and shifted and taxed curves) are 3.5 pt wide, axes 1.0 pt, equilibrium points 6.5 pt across, and figures have an opaque white background.
- Official examples use the `default` palette and no longer show legends or metric boxes. Example output always goes to `examples/output`, whichever directory the scripts run from.
- Curves are named directly beside their visible end instead of only in the legend. `MarketFigure.add_curves()`, comparative statics, tax transforms, externalities, common resources, trade (world and policy price), loanable funds, discrete schedules, the PPF canvases, the public-good canvas and the demand panel of the elasticity/revenue pair each add a MosaicKit `PointLabelLayer` (id `<curve id>.label`) whose text is the curve's legend label; MosaicKit places it beside the curve's end without covering any line, point, region or other text.
- Shifted and taxed curves use short symbols: `add_comparative_statics()` names them `D₁`/`S₁` (new `demand_label`/`supply_label` arguments), taxed curves are `S + t`/`D − t`, loanable-funds shifts are `D₁`/`S₁`, and social cost/benefit curves are `MSC`/`MSB`. Unshifted curves are no longer given a "(shifted)" legend entry.
- Welfare regions are named instead of lettered: `welfare_layers()` / `MarketFigure.add_welfare()` add a MosaicKit `RegionLabelLayer` per region ("Consumer surplus"/"CS", "Producer surplus"/"PS", "Tax revenue"/"Tax", "Deadweight loss"/"DWL") placed inside, by short name, or by callout. Pass `add_welfare(..., labels=False)` for shading only. `welfare_overlay_layers()` no longer draws A/B/C/D letters, and `LabeledRegion` now carries `key`, `label` and `short_label` instead of `letter`. Subsidy cost, tariff revenue / quota rent, externality and common-resource deadweight loss regions are named the same way. Calculations are unchanged.
- Axis titles default to `p` (price) and `Q` (quantity), set in italic math and placed past the arrow tips: the y title above its arrow, the x title to the right of its arrow (word titles end under the x arrow tip instead). Price marks are lowercase (`p_0`, `p_1^c`, `p_w`, `p∈[…]`).
- Titles use normal weight.
- Supply-and-demand figures are square (6 × 6 in at 150 dpi), and straight curves stop at 92% of the price axis so their names stay clear of the title.
- Equilibrium and policy labels (`$e^*$`, `$t = …$`, `$s = …$`) are point labels placed by MosaicKit beside their point. Crowded quantities are marked on the quantity axis instead, with a guide from the point: externality `$Q_m$`/`$Q^*$`, common resource `$Q^*$`/`$Q_{\mathrm{open}}$`, public good `$Q_p$`/`$Q^*$`.
- Binding price controls name the control line directly ("Price ceiling" / "Price floor"), mark `$p_c$` on the price axis and `$Q_d$`/`$Q_s$` on the quantity axis, and brace the gap on the control line itself, Mankiw style: "Shortage" below a ceiling, "Surplus" above a floor. `add_price_control(..., gap_brace="axis")` braces it under the quantity axis instead.
- A binding minimum wage is drawn the same way: the "Minimum wage" line, `$w_{\min}$`, `$L_d$`/`$L_s$`, and an "Unemployment" brace above the floor (`add_minimum_wage(..., gap_brace="axis")` for the axis). The unemployment arrow and the "= 9" value text are gone.
- Trade figures mark `$Q_s$`/`$Q_d$` and brace "Imports"/"Exports" under the quantity axis; the policy price is marked `$p_w + t$` (tariff) or `$p_q$` (quota).
- Corrective taxes and subsidies on externality diagrams span the gap between the private and social curve at `$Q^*$` (they were drawn from the wrong base), labelled `$t = …$` / `$s = …$`.
- The tax-rotation label is named at the arrow's tail, outside the wedge between the two curves.
- The PPF and public-good canvases no longer add legends.
- Example scripts use short titles and fewer hard-coded label offsets.
- Renamed the project from `principle-econ` to `principle-viz`, joining the EconViz family alongside `utility-viz` (the renamed `econ-viz`). The Python package is now `principle_viz`; the `principle-econ` PyPI distribution stops receiving updates as of v0.1.0.
- Switched project tooling from Poetry to uv (`pyproject.toml` now PEP 621 + `uv_build`, `uv.lock` replaces `poetry.lock`, CI and `scripts/release.sh` use `uv run`/`uv build`).

## v0.1.0 (2026-04-25)

### Features

- Build a modular package architecture for Principles of Economics linear market analysis:
  - `core` for lines/equilibrium/shifts/controls/elasticity
  - `policy` for tax models, incidence, comparisons, and visual guides
  - `welfare` for CS/PS/tax-revenue/TS/DWL and report helpers
  - `plot` for canvas/figure facade and focused renderers
  - `api` and `cli` facades
- Add tax support for fixed, per-unit, and ad valorem taxes, including consumer-side and producer-side legal incidence.
- Add tax transformation plotting semantics:
  - directional tax-shift arrows (`baseline -> policy`)
  - ad valorem proportional rotation overlays
- Add welfare transition overlays with baseline/policy guide lines and labeled regions (`A/B/C/...`).
- Add monochrome palette and support for `default`, `colorblind`, `nord`, and `monochrome` models.
- Add classroom examples grouped by topic under `examples/scripts/`.

### Tests

- Add unit tests across core, policy, welfare, and palette modules.
- Add plotting smoke tests for equilibrium, comparative statics, tax transforms, and welfare transitions.
- Add CLI smoke tests for equilibrium and tax commands.

### Tooling

- Manage package via Poetry (`pyproject.toml`, `poetry.lock`).
- Add lint/test setup with Ruff and Pytest.
- Add GitHub Actions workflow for CI + PyPI publishing via Trusted Publishing on tag pushes.
