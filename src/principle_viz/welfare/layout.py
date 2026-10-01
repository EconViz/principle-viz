"""Welfare annotation layout helpers."""

from __future__ import annotations

from dataclasses import dataclass

from principle_viz.welfare.surplus import MarketOutcome, SurplusResult


@dataclass(frozen=True)
class LabeledRegion:
    """Polygon region with a compact letter marker."""

    letter: str
    label: str
    points: tuple[tuple[float, float], ...]
    centroid: tuple[float, float]


@dataclass(frozen=True)
class WelfareReferenceLayout:
    """Reference guide lines for baseline and policy outcomes."""

    baseline_quantity: float
    policy_quantity: float
    baseline_price: float
    policy_consumer_price: float
    policy_producer_price: float


@dataclass(frozen=True)
class WelfareAnnotationLayout:
    """Combined welfare overlay layout for plotting."""

    reference: WelfareReferenceLayout
    regions: tuple[LabeledRegion, ...]


def _polygon_centroid(points: tuple[tuple[float, float], ...]) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    x_avg = sum(p[0] for p in points) / len(points)
    y_avg = sum(p[1] for p in points) / len(points)
    return (x_avg, y_avg)


def build_labeled_regions(surplus: SurplusResult) -> tuple[LabeledRegion, ...]:
    """Build compact A/B/C... region markers from welfare polygons."""
    raw_regions: tuple[tuple[str, tuple[tuple[float, float], ...]], ...] = (
        ("Consumer Surplus", surplus.polygons.consumer_surplus),
        ("Producer Surplus", surplus.polygons.producer_surplus),
        ("Tax Revenue", surplus.polygons.tax_revenue),
        ("Deadweight Loss", surplus.polygons.lost_surplus),
    )

    regions: list[LabeledRegion] = []
    next_letter = ord("A")
    for label, points in raw_regions:
        if not points:
            continue
        letter = chr(next_letter)
        next_letter += 1
        regions.append(
            LabeledRegion(
                letter=letter,
                label=label,
                points=points,
                centroid=_polygon_centroid(points),
            )
        )
    return tuple(regions)


def build_welfare_annotation_layout(
    baseline_outcome: MarketOutcome,
    policy_outcome: MarketOutcome,
    surplus: SurplusResult,
) -> WelfareAnnotationLayout:
    """Build reference guides and labeled welfare regions."""
    reference = WelfareReferenceLayout(
        baseline_quantity=baseline_outcome.quantity,
        policy_quantity=policy_outcome.quantity,
        baseline_price=baseline_outcome.consumer_price,
        policy_consumer_price=policy_outcome.consumer_price,
        policy_producer_price=policy_outcome.producer_price,
    )
    return WelfareAnnotationLayout(
        reference=reference, regions=build_labeled_regions(surplus)
    )


__all__ = [
    "LabeledRegion",
    "WelfareAnnotationLayout",
    "WelfareReferenceLayout",
    "build_labeled_regions",
    "build_welfare_annotation_layout",
]
