from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[1]


def test_all_example_scripts_execute() -> None:
    subprocess.run(
        [sys.executable, "examples/scripts/run_all.py"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    images = tuple((REPOSITORY_ROOT / "examples" / "output").rglob("*.png"))
    assert len(images) >= 20
    assert all(image.stat().st_size > 0 for image in images)
