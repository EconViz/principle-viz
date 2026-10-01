# Contributing to principle-viz

Thanks for your interest in improving `principle-viz`.

## Development Setup

```bash
git clone https://github.com/EconViz/principle-viz.git
cd principle-viz
uv sync
```

Run checks before opening a PR:

```bash
uv run ruff check src tests examples/scripts
uv run pytest -q
```

## Project Conventions

- Keep domain math plotting-agnostic (`core/`, `policy/`, `welfare/`).
- Keep plotting concerns inside `plot/` renderers and `MarketFigure` facade.
- Add tests for every behavior change.
- Keep examples image-only output under `examples/output/`.

## Do Not Commit Generated Files

This repository ignores generated artifacts (for example `examples/output/**`, caches, build directories).
Please do not force-add ignored files.

## Pull Request Checklist

- Add or update tests for your change.
- Run lint and test commands locally.
- Update `README.md` and/or `CHANGELOG.md` when behavior changes.
- Keep commits focused and easy to review.

## Issue Workflow

- Bug report: include a minimal reproducible case.
- Feature request: include teaching/use-case context and expected API.
- New contributors can start from issues with smaller scope and clear acceptance criteria.

## Release and PyPI

PyPI publish is handled by GitHub Actions Trusted Publishing:

- Workflow: `.github/workflows/publish.yml`
- Trigger: push a tag like `v0.1.0`

Helper script:

```bash
scripts/release.sh prepare 0.2.0
scripts/release.sh finalize 0.2.0
```

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
