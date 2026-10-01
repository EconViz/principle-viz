"""Economic curve geometry compiled to MosaicKit paths."""

from mosaickit import DashStyle, PathLayer, Stroke

from principle_viz.core.line import Line


def curve_layer(
    line: Line,
    *,
    q_min: float,
    q_max: float,
    layer_id: str,
    role: str,
    label: str | None = None,
    color: str | None = None,
    width: float | None = None,
    dash: DashStyle | str | None = None,
) -> PathLayer:
    stroke = None
    if color is not None or width is not None or dash is not None:
        stroke = Stroke(color=color, width=width, dash=dash)
    return PathLayer(
        ((float(q_min), line.p_at(q_min)), (float(q_max), line.p_at(q_max))),
        id=layer_id,
        role=role,
        legend=label,
        stroke=stroke,
        model=line,
        z_index=2,
    )


def segment_layer(
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    layer_id: str,
    role: str = "principle.market.guide",
    label: str | None = None,
    color: str | None = None,
    width: float | None = None,
    dash: DashStyle | str | None = None,
) -> PathLayer:
    stroke = None
    if color is not None or width is not None or dash is not None:
        stroke = Stroke(color=color, width=width, dash=dash)
    return PathLayer(
        (start, end), id=layer_id, role=role, legend=label, stroke=stroke, z_index=3
    )
