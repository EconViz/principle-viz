"""Custom exceptions for principle_viz."""


class PrincipleVizError(Exception):
    """Base exception for package errors."""


PrincipleEconError = PrincipleVizError


class LineError(PrincipleEconError):
    """Raised when a line cannot be constructed or transformed."""


class NonInvertibleLineError(LineError):
    """Raised when a line cannot be represented as P(Q) or Q(P)."""


class EquilibriumError(PrincipleEconError):
    """Raised when equilibrium cannot be solved."""


class ParallelLinesError(EquilibriumError):
    """Raised when no intersection exists due to parallel lines."""


class CoincidentLinesError(EquilibriumError):
    """Raised when infinitely many intersections exist."""


class PolicyError(PrincipleEconError):
    """Raised for invalid policy/scenario setup."""
