from __future__ import annotations

from pathlib import Path

SRC_ROOT = Path(__file__).parents[1] / "src"
MAX_LINES = 450


def test_no_source_file_exceeds_the_line_limit() -> None:
    too_long = {
        str(path.relative_to(SRC_ROOT)): count
        for path in sorted(SRC_ROOT.rglob("*.py"))
        if (count := len(path.read_text(encoding="utf-8").splitlines())) > MAX_LINES
    }
    assert not too_long, f"source files above {MAX_LINES} lines: {too_long}"
