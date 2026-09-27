from __future__ import annotations

import pytest

from principle_viz.core.line import Line
from principle_viz.exceptions import NonInvertibleLineError


def test_line_from_inverse_and_eval() -> None:
    line = Line.from_inverse(intercept=10.0, slope=-2.0)
    assert line.p_at(3.0) == pytest.approx(4.0)
    assert line.q_at(4.0) == pytest.approx(3.0)


def test_parallel_and_coincident() -> None:
    line_a = Line.from_inverse(10.0, -2.0)
    line_b = Line.from_inverse(8.0, -2.0)
    line_c = Line.from_standard(*line_a.as_tuple())

    assert line_a.is_parallel(line_b)
    assert line_a.is_coincident(line_c)


def test_vertical_line_to_inverse_raises() -> None:
    vertical = Line.from_standard(0.0, 1.0, -3.0)
    with pytest.raises(NonInvertibleLineError):
        vertical.to_inverse()
