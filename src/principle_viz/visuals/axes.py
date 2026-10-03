"""Market-axis layers."""

from mosaickit import ArrowPlacement, AxisSpec, Layer, TextLayer, build_axes

FIGURE_SIZE = {"width": 6.0, "height": 6.0, "dpi": 150}
"""Physical size of every principle-viz figure (one panel): square, so the price and
quantity axes have the same length, as in textbook supply-and-demand diagrams."""

TITLE_GAP_PT = 6.0
"""Gap between an arrow tip and its axis title, in points."""


def _is_symbol(label: str) -> bool:
    """Single-letter titles (p, Q, w, L) and ``$...$`` titles are set as math;
    words stay upright."""
    is_math = len(label) > 1 and label.startswith("$") and label.endswith("$")
    return is_math or (len(label) == 1 and label.isalpha())


def axis_title_layers(
    x_max: float, y_max: float, *, x_label: str, y_label: str
) -> tuple[TextLayer, ...]:
    """Axis titles past the arrow tips: y above its arrow, x to the right of its arrow."""
    layers: list[TextLayer] = []
    if y_label:
        layers.append(
            TextLayer(
                (0.0, float(y_max)),
                y_label,
                id="axes.y.label",
                role="axes",
                offset=(0, TITLE_GAP_PT),
                anchor="bottom",
                math=_is_symbol(y_label),
            )
        )
    if x_label:
        symbol = _is_symbol(x_label)
        # A symbol sits right of the tip; a word would run off the figure there,
        # so it ends at the tip, under the arrow.
        layers.append(
            TextLayer(
                (float(x_max), 0.0),
                x_label,
                id="axes.x.label",
                role="axes",
                offset=(TITLE_GAP_PT, 0) if symbol else (0, -TITLE_GAP_PT),
                anchor="left" if symbol else "top-right",
                math=symbol,
            )
        )
    return tuple(layers)


def market_axes_layers(
    x_max: float,
    y_max: float,
    *,
    x_label: str,
    y_label: str,
    arrows: bool = True,
    origin_label: bool = True,
) -> tuple[Layer, ...]:
    arrow = ArrowPlacement.END if arrows else None
    layers = list(
        build_axes(
            AxisSpec((0.0, float(x_max)), arrow=arrow),
            AxisSpec((0.0, float(y_max)), arrow=arrow),
        )
    )
    layers.extend(axis_title_layers(x_max, y_max, x_label=x_label, y_label=y_label))
    if origin_label:
        layers.append(
            TextLayer(
                (0.0, 0.0),
                "0",
                id="axes.origin.label",
                role="axes",
                offset=(-7, -7),
                anchor="right",
            )
        )
    return tuple(layers)
