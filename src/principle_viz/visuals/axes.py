"""Market-axis layers."""

from mosaickit import ArrowPlacement, AxisSpec, Layer, TextLayer, build_axes


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
            AxisSpec((0.0, float(x_max)), arrow=arrow, label=x_label),
            AxisSpec((0.0, float(y_max)), arrow=arrow, label=y_label),
        )
    )
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
