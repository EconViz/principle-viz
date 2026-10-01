"""Welfare metrics and reporting."""

from principle_viz.welfare.discrete import (
    DiscreteSurplusResult,
    compute_discrete_surplus,
)
from principle_viz.welfare.layout import (
    LabeledRegion,
    WelfareAnnotationLayout,
    WelfareReferenceLayout,
    build_labeled_regions,
    build_welfare_annotation_layout,
)
from principle_viz.welfare.report import (
    DWLScenarioRow,
    build_dwl_report,
    save_dwl_report_csv,
    save_dwl_report_json,
)
from principle_viz.welfare.surplus import (
    MarketOutcome,
    SurplusDeltaResult,
    SurplusPolygons,
    SurplusResult,
    compare_surplus,
    compute_surplus,
    outcome_from_control,
    outcome_from_equilibrium,
    outcome_from_tax,
)

__all__ = [
    "DWLScenarioRow",
    "DiscreteSurplusResult",
    "LabeledRegion",
    "MarketOutcome",
    "SurplusDeltaResult",
    "SurplusPolygons",
    "SurplusResult",
    "WelfareAnnotationLayout",
    "WelfareReferenceLayout",
    "build_dwl_report",
    "build_labeled_regions",
    "build_welfare_annotation_layout",
    "compare_surplus",
    "compute_discrete_surplus",
    "compute_surplus",
    "outcome_from_control",
    "outcome_from_equilibrium",
    "outcome_from_tax",
    "save_dwl_report_csv",
    "save_dwl_report_json",
]
