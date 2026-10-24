# CHANGELOG

All notable changes to this project are documented in this file.

## v0.14.0 (2026-10-24)

### Added

- `[principle.label.<group>]` in `econ-viz.toml` moves whole groups of labels by default. Each
  group takes `top`, `bottom`, `left` and `right` (lengths in pt, mm, cm or in, validated like
  utility-viz's nudges; `em` is not accepted; default no move). The groups: `point` (equilibrium
  and PPF point labels such as `e_0`, `e^*`, `L^*`), `curve` (`D`, `S`, `D_1`, `S + t`, `MSB`, `MSC`,
  `MC`, `PPF`, ...), `region` (consumer/producer surplus, deadweight loss, tax and tariff revenue,
  subsidy cost, callouts included), `mark` (`p_c`, `w_min`, `p_w` and the `t = ...` / `s = ...`
  wedges) and `annotation` (brace labels, metrics and other text). Axis labels belong to no group.
- `PlotTheme.label_nudges` (group name to mosaickit `Nudge`) carries the defaults, and
  `principle_viz.label_groups.label_group(layer)` tells which group a label layer is in.
- A label with its own `Label(top=, bottom=, left=, right=)` is moved by those values only: the
  per-label nudge replaces the group default instead of adding to it. A `Label` that only renames,
  hides or offsets a label keeps the default. Figures without these settings are unchanged.

## v0.13.0 (2026-10-24)

### Added

- The figure title is a parameter instead of fixed text: `ppf_canvas`, `ppf_growth_canvas` and
  `public_good_canvas` take `title=` (default unchanged, `None` draws no title), and
  `elasticity_revenue_canvases` takes `titles=(demand_title, revenue_title)`. A title that is a
  built-in English phrase is still translated by the figure's language; any other text is drawn as
  given.

## v0.12.1 (2026-10-23)

### Added

- `Label` takes `top`, `bottom`, `left` and `right`: lengths that move one label after it has been
  placed, e.g. `MarketFigure(labels={"market.equilibrium": Label(top="4pt")})` or
  `figure.configure_label("market.supply", Label(right="8pt"))` (`configure_label` also takes them
  as keywords). A length is a number of points or a string such as `"10pt"`, `"0.5em"` (the label's
  font size) or `"2mm"`. They become a mosaickit `Nudge` on the label layer; `Label(offset=...)`
  keeps its behaviour and a nudge applies after it. Figures without nudges are unchanged. There is
  no `[principle.label]` default in `econ-viz.toml` yet.

### Changed

- `econ-viz.toml` is read by mosaickit: principle-viz declares its `[principle]` table as a
  `mosaickit.econ_toml.Schema` and has no parser of its own. `Config`, `default_theme()` and the
  figures behave as before, and the same file gives the same figures.
- The colour models are mosaickit's shared themes: `manual`, `default`, `colorblind`, `monochrome`,
  `nord`, `paper` and `presentation` (the last two are new here). `principle_viz.visuals.roles` maps
  each element to a theme role (axis, label, baseline and arrow to ink; demand to primary; supply
  to secondary; shifted to tertiary; tax and control to intervention; consumer surplus, producer
  surplus, deadweight loss and tax revenue to the light, mid, dark and faint fills) and builds the
  colour models and plot themes from the tokens. The theme's line and marker scales multiply
  principle-viz's line widths and equilibrium dot. `get_color_model`, `list_color_models` and
  `PlotTheme.from_palette` take the same names.
- `manual` is unchanged. The other themes change colour: demand takes the primary colour and supply
  the secondary, and the fills follow the curves. In `default`, demand is `#377EB8` (was the
  palette's `blue`), supply `#4DAF4A` (was `red`), shifted curves `#777777`, tax and price controls
  `#FF7F00`, and consumer surplus, producer surplus, deadweight loss and tax revenue `#377EB8`,
  `#4DAF4A`, `#E41A1C` and `#FF7F00`; `default` no longer names mosaickit palette colours, so a
  `[palette]` override no longer recolours it. `colorblind` now matches `default`, `nord` and
  `monochrome` reassign their roles the same way (e.g. nord supply `#A3BE8C`, was `#BF616A`;
  monochrome demand and supply both `#000000`).
- The shared `base` picks principle-viz's starting theme. `[principle] palette` still works and
  wins over `base` for principle-viz (it sets the colours only).
- Mistakes are reported in mosaickit's format, naming the file and the table and suggesting the
  closest key, e.g. `econ-viz.toml: [principle.color] unknown key 'demnad'; did you mean 'demand'?`.
  Colours are now checked (`#rgb`, `#rrggbb`, `#rrggbbaa` or a colour name), and unknown top-level
  keys are errors. utility-viz's tables, under `[utility]` or at the old top level, are skipped.
- principle-viz registers its `Config` under the `econviz.config` entry point, so
  `mosaickit.econ_toml.use()` loads it with the other installed packages.
- Requires `mosaickit>=1.0.0rc6`.

## v0.12.0 (2026-10-23)

### Added

- `Config.load("econ-viz.toml").use()` reads the settings file every EconViz package shares:
  fonts, the math font and the axis and label colours from the shared sections, and principle-viz's
  own settings from the `[principle]` table (`palette`, `language`, `[principle.color]`,
  `[principle.stroke]`, `[principle.marker]`). Figures made without `theme=` or `palette=` then use
  it; `default_theme()` returns the theme they get. Sections of other packages are skipped.

### Changed

- Requires `mosaickit>=1.0.0rc5`, which reads the shared sections.

## v0.11.2 (2026-10-22)

### Added

- `palette="manual"`: the greys of the principle-viz manual (black axes, supply and arrows, a grey
  demand curve, grey surplus regions), the same look as utility-viz's manual figures.
- `PlotTheme(language=...)`: `"en"` (the default), `"zh-TW"` or `"zh-CN"`. Built-in figure text such
  as "Shortage", "Consumer surplus" and panel titles is drawn in that language, from the table the
  manual's Chinese editions use. Text you set through `labels=` or `configure_label` is kept as
  written. Chinese text needs a font with the characters, e.g. `fonts=TextFonts(serif=...)`.

### Changed

- Requires `mosaickit>=1.0.0rc3,<2.0.0`, which sets panel titles and text mixed with math in the
  configured fonts, so Chinese titles render instead of boxes.

## v0.11.1 (2026-10-22)

### Changed

- Requires `mosaickit>=1.0.0rc2,<2.0.0` (was `>=0.9.2,<0.10.0`). MosaicKit 1.0.0rc2 places labels on
  arrays and caches mathtext while a figure is drawn, which makes the market diagrams about 1.4x
  faster with byte-identical output (measured on the eight benchmark diagrams). The test suite
  passes unchanged.

## v0.11.0 (2026-10-21)

### Changed

- Fonts behave as in every diagram package built on MosaicKit. `PlotTheme(font=...)` is `"sans"` (the
  default), `"serif"` or `"mono"`; `PlotTheme(fonts=TextFonts(...))` replaces any of the three with
  your font files and the rest keep the defaults; `PlotTheme(math_font=...)` takes a `MathFont` or the
  path of an OpenType math font, and without it math is set by Matplotlib.
  `PlotTheme(font_roles={...})` gives one role, such as `principle.market.demand`, its own generic font.
- Requires `mosaickit>=0.9.2,<0.10.0`.

## v0.10.2 (2026-10-20)

### Changed

- Requires `mosaickit>=0.8.0,<0.9.0` (was `>=0.5.1,<0.6.0`). The test suite passes unchanged on 0.8.0, also with `DeprecationWarning` treated as an error. MosaicKit 0.6 deprecates `TextStyle.weight` in favour of GlyphKit but has no other way to set bold text yet, so the theme keeps its two bold/normal weights and silences that one warning where it builds them.

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
