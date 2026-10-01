"""Line domain model for linear demand/supply equations."""

from __future__ import annotations

import math
from dataclasses import dataclass

from principle_viz.exceptions import LineError, NonInvertibleLineError

EPSILON = 1e-9


@dataclass(frozen=True)
class Line:
    """Represents A*P + B*Q + C = 0."""

    p_coef: float
    q_coef: float
    constant: float

    def __post_init__(self) -> None:
        values = (self.p_coef, self.q_coef, self.constant)
        if not all(math.isfinite(v) for v in values):
            raise LineError("Line coefficients must be finite numbers.")
        if abs(self.p_coef) < EPSILON and abs(self.q_coef) < EPSILON:
            raise LineError("At least one of p_coef or q_coef must be non-zero.")

    @classmethod
    def from_inverse(cls, intercept: float, slope: float) -> Line:
        """Construct line from P = intercept + slope*Q."""
        return cls(p_coef=1.0, q_coef=-float(slope), constant=-float(intercept))

    @classmethod
    def from_standard(cls, a: float, b: float, c: float) -> Line:
        """Construct line from A*P + B*Q + C = 0."""
        return cls(p_coef=float(a), q_coef=float(b), constant=float(c))

    def to_inverse(self) -> tuple[float, float]:
        """Return intercept, slope for P = intercept + slope*Q."""
        if abs(self.p_coef) < EPSILON:
            raise NonInvertibleLineError("Vertical line cannot be represented as P(Q).")
        intercept = -self.constant / self.p_coef
        slope = -self.q_coef / self.p_coef
        return intercept, slope

    def p_at(self, q: float) -> float:
        """Evaluate P at a given Q."""
        intercept, slope = self.to_inverse()
        return intercept + slope * float(q)

    def q_at(self, p: float) -> float:
        """Evaluate Q at a given P."""
        if abs(self.q_coef) < EPSILON:
            raise NonInvertibleLineError(
                "Horizontal line cannot be represented as Q(P)."
            )
        return (-self.p_coef * float(p) - self.constant) / self.q_coef

    def shifted(self, delta_intercept: float = 0.0, delta_slope: float = 0.0) -> Line:
        """Return shifted/rotated line in inverse-space coordinates."""
        intercept, slope = self.to_inverse()
        return Line.from_inverse(intercept + delta_intercept, slope + delta_slope)

    def is_parallel(self, other: Line, tol: float = EPSILON) -> bool:
        """True when lines have no unique intersection due to equal direction."""
        det = self.p_coef * other.q_coef - other.p_coef * self.q_coef
        return abs(det) <= tol

    def is_coincident(self, other: Line, tol: float = EPSILON) -> bool:
        """True when both equations represent the same infinite line."""
        cross_ab = self.p_coef * other.q_coef - other.p_coef * self.q_coef
        cross_ac = self.p_coef * other.constant - other.p_coef * self.constant
        cross_bc = self.q_coef * other.constant - other.q_coef * self.constant
        return abs(cross_ab) <= tol and abs(cross_ac) <= tol and abs(cross_bc) <= tol

    def slope(self) -> float:
        """Return dP/dQ when defined."""
        _, slope = self.to_inverse()
        return slope

    def p_intercept(self) -> float:
        """Return P-intercept at Q=0."""
        intercept, _ = self.to_inverse()
        return intercept

    def q_intercept(self) -> float:
        """Return Q-intercept at P=0 when defined."""
        return self.q_at(0.0)

    def as_tuple(self) -> tuple[float, float, float]:
        """Return coefficient tuple."""
        return self.p_coef, self.q_coef, self.constant
