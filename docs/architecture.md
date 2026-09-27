# Principle-Viz Architecture

## Scope
This package focuses on linear demand and supply analysis for Principles of Economics use cases:
- equilibrium solving
- comparative statics
- taxes and legal incidence
- price controls
- welfare decomposition and deadweight loss reporting
- publication-ready instructional plots

## Layered Structure
- `principle_viz.core`: immutable line domain, equilibrium solving, shifts, elasticity, and controls.
- `principle_viz.policy`: tax policy layer split by responsibility.
  - `models.py`: enums + dataclasses (`TaxScenario`, `TaxEquilibriumResult`, etc.)
  - `solver.py`: numerical/equation solving for fixed/per-unit/ad valorem taxes
  - `analysis.py`: baseline-vs-policy comparison logic
  - `tax.py`: compatibility facade for public imports
- `principle_viz.welfare`: surplus metrics, welfare delta decomposition, and DWL reports.
- `principle_viz.plot`: figure facade and focused renderer modules.
- `principle_viz.api`: high-level API aggregating core/policy/welfare/plot helpers.
- `principle_viz.cli`: command-line interface for reproducible scenarios.

## Design Rules
- Core math is plotting-agnostic.
- Plotting modules consume typed result objects; they do not solve economic models.
- CLI only orchestrates API calls and serialization.
- Unit tests cover model and solver logic; smoke tests cover plotting and CLI execution paths.

## Data Flow
1. Build line models from user inputs.
2. Solve equilibrium or policy scenario.
3. Compute welfare metrics and deltas.
4. Render and export figures or reports.
5. Optionally serialize results through CLI JSON output.
