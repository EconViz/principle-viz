"""Metrics annotations."""

from mosaickit import TextLayer

_LOCATIONS: dict[str, tuple[float, float, str]] = {
    "upper right": (0.98, 0.98, "right"),
    "upper left": (0.02, 0.98, "left"),
    "lower right": (0.98, 0.02, "right"),
    "lower left": (0.02, 0.02, "left"),
}


def _format_metric(value: object) -> str:
    return f"{value:.3f}" if isinstance(value, float) else str(value)


def metrics_layer(
    metrics: dict[str, object],
    *,
    x_max: float,
    y_max: float,
    layer_id: str = "market.metrics",
    title: str | None = None,
    location: str = "upper right",
) -> TextLayer:
    x_fraction, y_fraction, anchor = _LOCATIONS.get(location, _LOCATIONS["upper right"])
    lines: list[str] = []
    if title:
        lines.extend((title, "—"))
    lines.extend(f"{key}: {_format_metric(value)}" for key, value in metrics.items())
    return TextLayer(
        (x_fraction * x_max, y_fraction * y_max),
        "\n".join(lines),
        id=layer_id,
        role="principle.annotation",
        anchor=anchor,
        z_index=10,
    )
