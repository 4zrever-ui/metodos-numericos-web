"""
Shared data models for all numerical method results.
Structure mirrors the Excel file exactly.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IterationRow:
    k: int
    x_new: float           # The key approximation (c for interval, x_{n+1} for point)
    error_pct: Optional[float]      # Relative % error (None for k=0 in some methods)
    converged: Optional[bool]       # None for k=0 in some methods
    extra: dict = field(default_factory=dict)  # method-specific columns


@dataclass
class MethodResult:
    method_name: str
    applicable: bool
    reason: str            # why applicable or not
    equation_str: str
    f_latex: str
    fp_latex: str
    fpp_latex: str
    params_used: dict      # a, b, x0, tol, gx, etc.
    iterations: list[IterationRow]
    root: Optional[float]
    final_error_pct: Optional[float]
    converged: bool
    iteration_count: int
    excel_sheet_name: str
    formula_description: str


# ── Interval methods ──────────────────────────────────────────────────────────

@dataclass
class IntervalRow(IterationRow):
    a: float = 0.0
    c: float = 0.0
    b: float = 0.0
    fa: float = 0.0
    fc: float = 0.0
    fb: float = 0.0
    fa_fc: float = 0.0


# ── Point-iteration methods ───────────────────────────────────────────────────

@dataclass
class FixedPointRow(IterationRow):
    xk: float = 0.0
    gxk: float = 0.0


@dataclass
class AitkenRow(IterationRow):
    p0: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    xk_hat: float = 0.0   # Aitken accelerated value


@dataclass
class SteffensenRow(IterationRow):
    p0: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    xk_hat: float = 0.0


# ── Derivative methods ────────────────────────────────────────────────────────

@dataclass
class NewtonRaphsonRow(IterationRow):
    xk: float = 0.0
    fxk: float = 0.0
    fpxk: float = 0.0
    x_next: float = 0.0


@dataclass
class NewtonModRow(IterationRow):
    xk: float = 0.0
    fxk: float = 0.0
    fpxk: float = 0.0
    fppxk: float = 0.0
    x_next: float = 0.0


@dataclass
class SecantRow(IterationRow):
    xk: float = 0.0
    fxk: float = 0.0
    xk_prev: Optional[float] = None
    fxk_prev: Optional[float] = None
    x_next: Optional[float] = None


@dataclass
class VonMisesRow(IterationRow):
    xk: float = 0.0
    fxk: float = 0.0
    fp_x0: float = 0.0
    x_next: float = 0.0