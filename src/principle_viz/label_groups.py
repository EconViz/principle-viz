"""Which group a PrincipleViz label belongs to, for the label nudges in ``econ-viz.toml``.

``[principle.label.<group>]`` moves every label of a group by default. The groups follow
what a label names:

``point``
    Dots: equilibrium labels (``e_0``, ``e^*``, ``e_1``, ``e_t``, ``L^*``, the discrete
    ``Q^* = ..., p^* = ...``) and the labelled points of a production possibilities
    frontier.
``curve``
    Curves named beside their end: demand and supply (``D``, ``S``, ``D_1``, ``S + t``,
    ``MSB``, ``MSC``, ``MC``, ``\\Sigma MB``, the curves of an aggregation or a public
    good) and production possibilities frontiers (``PPF``, ``PPF_0``, ``PPF_1``).
``region``
    Names inside filled regions, including those drawn as a callout with a leader line:
    consumer and producer surplus, deadweight loss, tax revenue, subsidy cost, tariff
    revenue.
``mark``
    Price lines and policy marks: ``p_c``, ``w_{\\min}``, ``p_w``, ``p_w + t``, the
    ``t = ...``, ``s = ...`` and ``f = ...`` wedges, and the ``t = ...`` of a tax shift.
``annotation``
    Everything else that is text: brace labels (Shortage, Tax, Subsidy, Imports,
    Unemployment), price intervals, metrics and the elasticity zone names.

Axis labels (the axis names, the origin, axis marks such as ``Q_0`` and ``p_1`` and their
notes) belong to no group: they cannot be nudged.
"""

from __future__ import annotations

from mosaickit import (
    AxisMarkLayer,
    AxisNoteLayer,
    BraceLayer,
    Layer,
    PointLabelLayer,
    RegionLabelLayer,
    SpanBraceLayer,
    TextLayer,
)

LABEL_GROUPS = ("point", "curve", "region", "mark", "annotation")
"""The label groups, in the order of ``[principle.label.<group>]``."""

LABEL_SIDES = ("top", "bottom", "left", "right")
"""The directions of a nudge, as in ``Label(top=, bottom=, left=, right=)``."""

_POINT_ROLES = ("principle.market.equilibrium",)
_CURVE_ROLES = (
    "principle.market.demand",
    "principle.market.supply",
    "principle.ppf.frontier",
    "principle.ppf.shifted",
)
_MARK_ROLES = ("principle.policy", "principle.trade", "principle.market.movement")


def _under(role: str, roles: tuple[str, ...]) -> bool:
    return any(role == prefix or role.startswith(f"{prefix}.") for prefix in roles)


def label_group(layer: Layer) -> str | None:
    """The group of ``layer``'s label, or ``None`` for one that takes no default nudge."""
    if isinstance(layer, (AxisMarkLayer, AxisNoteLayer)):
        return None
    if isinstance(layer, RegionLabelLayer):
        return "region"
    if isinstance(layer, PointLabelLayer):
        if _under(layer.role, _POINT_ROLES) or layer.id.startswith("ppf.point."):
            return "point"
        if _under(layer.role, _CURVE_ROLES):
            return "curve"
        if _under(layer.role, _MARK_ROLES):
            return "mark"
        return "annotation"
    if isinstance(layer, TextLayer):
        return None if layer.id.startswith("axes.") else "annotation"
    if isinstance(layer, (BraceLayer, SpanBraceLayer)):
        return "annotation"
    return None


__all__ = ["LABEL_GROUPS", "LABEL_SIDES", "label_group"]
