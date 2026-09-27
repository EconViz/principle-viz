from __future__ import annotations

from principle_viz.plot.canvas import Canvas


def test_canvas_uses_first_quadrant_and_no_top_right_spines() -> None:
    canvas = Canvas(x_max=10.0, y_max=8.0, title=None)

    x0, x1 = canvas.ax.get_xlim()
    y0, y1 = canvas.ax.get_ylim()

    assert x0 == 0.0
    assert y0 == 0.0
    assert x1 == 10.0
    assert y1 == 8.0

    assert canvas.ax.spines["top"].get_visible() is False
    assert canvas.ax.spines["right"].get_visible() is False

    assert any(text.get_text() == "0" for text in canvas.ax.texts)

    canvas.close()


def test_canvas_has_no_grid_by_default() -> None:
    canvas = Canvas(x_max=10.0, y_max=10.0, title=None)

    x_grid_visible = any(line.get_visible() for line in canvas.ax.get_xgridlines())
    y_grid_visible = any(line.get_visible() for line in canvas.ax.get_ygridlines())

    assert x_grid_visible is False
    assert y_grid_visible is False

    canvas.close()


def test_canvas_legend_is_square_when_enabled() -> None:
    canvas = Canvas(x_max=10.0, y_max=10.0, title=None)
    canvas.ax.plot([0.0, 1.0], [0.0, 1.0], label="Line")
    canvas.finalize(legend=True)

    legend = canvas.ax.get_legend()
    assert legend is not None
    assert type(legend.get_frame().get_boxstyle()).__name__ == "Square"

    canvas.close()
