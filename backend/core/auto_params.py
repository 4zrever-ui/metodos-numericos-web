"""
Auto-parameter generator.
Finds roots, valid intervals [a,b], initial approximations, and g(x) candidates.
Priority: positive integers → non-negative integers → negative integers → decimals.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import sympy as sp

from .equation_parser import ParsedEquation, eval_f, eval_fp, eval_fpp

_x = sp.Symbol("x")

_SEARCH_RANGE = [
    *range(1, 11),
    *range(0, -11, -1),
    *[i / 2 for i in range(-21, 22)],
]


@dataclass
class AutoParams:
    a: float                        # interval left
    b: float                        # interval right
    x0: float                       # single initial approximation
    x0_alt: float                   # second initial approximation (for Secante)
    x0_von_mises: float             # x0 for Von Mises (same as x0)
    tol: float                      # convergence tolerance (matches Excel: 0.00001)
    max_iter: int                   # maximum iterations
    gx_sympy: Optional[sp.Expr]     # selected g(x)
    gx_excel: str                   # g(x) as Excel formula pattern
    gx_latex: str                   # g(x) latex
    gx_candidates: list[dict]       # all candidates with convergence info
    roots_approx: list[float]       # approximate roots found
    f_sign_change_found: bool


def _candidate_integers(values: list) -> list:
    out = []
    # Positive integers first
    out += [v for v in values if isinstance(v, int) and v > 0]
    # Zero
    out += [v for v in values if v == 0]
    # Negative integers
    out += [v for v in values if isinstance(v, int) and v < 0]
    # Floats
    out += [v for v in values if isinstance(v, float)]
    return out


def _find_sign_changes(eq: ParsedEquation, xs: list[float]) -> list[tuple[float, float]]:
    pairs = []
    for i in range(len(xs) - 1):
        try:
            fa = eval_f(eq, xs[i])
            fb = eval_f(eq, xs[i + 1])
            if math.isfinite(fa) and math.isfinite(fb) and fa * fb < 0:
                pairs.append((xs[i], xs[i + 1]))
        except Exception:
            continue
    return pairs


def _bisect_approx(eq: ParsedEquation, a: float, b: float, steps: int = 50) -> float:
    for _ in range(steps):
        c = (a + b) / 2
        fc = eval_f(eq, c)
        fa = eval_f(eq, a)
        if abs(fc) < 1e-12:
            return c
        if fa * fc < 0:
            b = c
        else:
            a = c
    return (a + b) / 2


def _generate_gx_candidates(eq: ParsedEquation, root: float) -> list[dict]:
    """
    Generate algebraically equivalent g(x) from f(x) = 0.
    Evaluate |g'(x)| at root to rank convergence.

    Strategy S1: g(x) = x - f(x)/f'(x)
      Applied when f'(root) != 0 and the simplified expression is valid.
      |g'(root)| = |f(root)·f''(root)| / |f'(root)|^2.
      Near the root f(root)≈0, so |g'(root)|≈0 < 1 — guaranteed convergence.
    """
    candidates = []
    f = eq.f_sympy
    x = _x

    # Strategy S1: g(x) = x - f(x)/f'(x)
    try:
        fp_root = eval_fp(eq, root)
        if abs(fp_root) > 1e-10:
            fp_sym = eq.fp_sympy
            g1 = x - f / fp_sym
            g1s = sp.simplify(g1)
            gp1 = sp.diff(g1s, x)
            gp1_val = abs(float(gp1.subs(x, root).evalf()))
            if math.isfinite(gp1_val):
                candidates.append({
                    "expr": g1s,
                    "label": "x - f(x)/f'(x)",
                    "gp_abs": gp1_val,
                    "converges": gp1_val < 1,
                })
    except Exception:
        pass

    # Sort: converging first, then by |g'(x)| ascending
    candidates.sort(key=lambda c: (0 if c["converges"] else 1, c["gp_abs"]))

    return candidates


def generate_params(eq: ParsedEquation) -> AutoParams:
    # Build search grid
    grid_ints = list(range(-15, 16))
    grid_fine = [i * 0.5 for i in range(-30, 31)]
    grid = sorted(set(grid_ints + grid_fine))

    # Find sign changes
    sign_changes = _find_sign_changes(eq, grid)
    f_sign_change_found = len(sign_changes) > 0

    roots_approx: list[float] = []
    if sign_changes:
        for a, b in sign_changes[:4]:
            root = _bisect_approx(eq, a, b)
            roots_approx.append(round(root, 10))

    # Try sympy solve for exact roots
    try:
        exact_roots = sp.solve(eq.f_sympy, _x)
        for r in exact_roots:
            try:
                rv = float(r.evalf())
                if math.isfinite(rv) and not any(abs(rv - er) < 1e-6 for er in roots_approx):
                    roots_approx.append(rv)
            except Exception:
                pass
    except Exception:
        pass

    if not roots_approx:
        # Fallback: scan for minimum |f(x)|
        vals = [(abs(eval_f(eq, v)), v) for v in grid if math.isfinite(eval_f(eq, v))]
        if vals:
            vals.sort()
            roots_approx = [vals[0][1]]

    # Select best [a, b] — prefer integers
    a, b = 1.0, 2.0
    if sign_changes:
        # Pick the sign-change pair where both endpoints are smallest positive integers
        def pair_score(pair):
            av, bv = pair
            is_pos_int = lambda v: v == int(v) and v > 0
            score = 0
            if is_pos_int(av): score += 0
            elif av >= 0 and av == int(av): score += 1
            elif av < 0 and av == int(av): score += 2
            else: score += 3
            if is_pos_int(bv): score += 0
            elif bv >= 0 and bv == int(bv): score += 1
            elif bv < 0 and bv == int(bv): score += 2
            else: score += 3
            return score

        sign_changes.sort(key=pair_score)
        a, b = sign_changes[0]

    # Select x0 — closest integer to first root, skipping points where f'≈0
    root_ref = roots_approx[0] if roots_approx else 1.0
    x0 = _best_integer_near(root_ref, eq=eq)
    x0_alt = _best_integer_near(root_ref, exclude=x0, eq=eq)

    # g(x) candidates
    gx_candidates = _generate_gx_candidates(eq, root_ref) if roots_approx else []

    # Select best g(x)
    gx_sympy = None
    gx_excel = ""
    gx_latex = ""
    if gx_candidates:
        best = gx_candidates[0]
        gx_sympy = best["expr"]
        gx_latex = sp.latex(gx_sympy)
        from .equation_parser import _sympy_to_excel
        gx_excel = _sympy_to_excel(gx_sympy)

    return AutoParams(
        a=a,
        b=b,
        x0=x0,
        x0_alt=x0_alt,
        x0_von_mises=x0,
        tol=0.00001,
        max_iter=25,
        gx_sympy=gx_sympy,
        gx_excel=gx_excel,
        gx_latex=gx_latex,
        gx_candidates=[
            {
                "label": c["label"],
                "gp_abs": c["gp_abs"],
                "converges": c["converges"],
                "latex": sp.latex(c["expr"]),
                "expr": str(c["expr"]),
            }
            for c in gx_candidates
        ],
        roots_approx=roots_approx,
        f_sign_change_found=f_sign_change_found,
    )


def _best_integer_near(
    val: float,
    exclude: Optional[float] = None,
    eq: Optional[object] = None,
) -> float:
    """Return the best integer near val, preferring positive, excluding one value.

    When eq is provided, candidates where |f'(c)| < 1e-10 are deprioritized
    (pushed to the back of the sort) so derivative-based methods can start
    from a valid point.  Falls back to a zero-derivative candidate only if
    no valid alternative exists.
    """
    candidates = [
        math.floor(val),
        math.ceil(val),
        round(val),
        math.floor(val) - 1,
        math.ceil(val) + 1,
    ]
    # Deduplicate while preserving order, removing excluded value
    seen: set = set()
    filtered = []
    for c in candidates:
        if (exclude is None or c != exclude) and c not in seen:
            seen.add(c)
            filtered.append(c)
    candidates = filtered

    def sort_key(c: int) -> tuple:
        sign_prio = 0 if c > 0 else (1 if c == 0 else 2)
        dist = abs(c - val)
        fp_penalty = 0
        if eq is not None:
            try:
                fp_val = abs(eval_fp(eq, float(c)))
                if fp_val < 1e-10:
                    fp_penalty = 10
            except Exception:
                pass
        return (fp_penalty, sign_prio, dist)

    candidates.sort(key=sort_key)
    return float(candidates[0]) if candidates else val