"""Elasticity calculations for linear equations."""

from __future__ import annotations

from principle_viz.core.line import EPSILON, Line
from principle_viz.exceptions import LineError


def point_price_elasticity(line: Line, q: float, tol: float = EPSILON) -> float:
    """Compute point price elasticity of quantity with respect to price."""
    intercept, slope = line.to_inverse()
    if abs(slope) <= tol:
        raise LineError("Point elasticity is undefined for zero slope.")
    q = float(q)
    if abs(q) <= tol:
        raise LineError("Point elasticity is undefined at Q=0.")
    p = intercept + slope * q
    return (p / q) / slope



def arc_price_elasticity(q0: float, p0: float, q1: float, p1: float, tol: float = EPSILON) -> float:
    """Compute arc elasticity between two points."""
    q0 = float(q0)
    q1 = float(q1)
    p0 = float(p0)
    p1 = float(p1)

    q_avg = 0.5 * (q0 + q1)
    p_avg = 0.5 * (p0 + p1)
    dq = q1 - q0
    dp = p1 - p0

    if abs(q_avg) <= tol or abs(p_avg) <= tol or abs(dp) <= tol:
        raise LineError("Arc elasticity is undefined for zero midpoint or zero price change.")

    return (dq / q_avg) / (dp / p_avg)



def classify_elasticity(value: float, tol: float = EPSILON) -> str:
    """Classify absolute elasticity magnitude."""
    abs_val = abs(float(value))
    if abs(abs_val - 1.0) <= tol:
        return "unit_elastic"
    if abs_val > 1.0:
        return "elastic"
    return "inelastic"
