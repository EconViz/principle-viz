from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[1] / "src" / "principle_viz"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_principle_viz_never_imports_matplotlib() -> None:
    offenders = {
        path.relative_to(PACKAGE_ROOT): sorted(
            name
            for name in _imports(path)
            if name == "matplotlib" or name.startswith("matplotlib.")
        )
        for path in PACKAGE_ROOT.rglob("*.py")
        if any(
            name == "matplotlib" or name.startswith("matplotlib.")
            for name in _imports(path)
        )
    }
    assert offenders == {}


def test_economic_domain_does_not_import_mosaickit() -> None:
    domain_roots = (
        PACKAGE_ROOT / "core",
        PACKAGE_ROOT / "policy",
        PACKAGE_ROOT / "welfare",
    )
    offenders = {
        path.relative_to(PACKAGE_ROOT): sorted(
            name
            for name in _imports(path)
            if name == "mosaickit" or name.startswith("mosaickit.")
        )
        for root in domain_roots
        for path in root.rglob("*.py")
        if any(
            name == "mosaickit" or name.startswith("mosaickit.")
            for name in _imports(path)
        )
    }
    assert offenders == {}
