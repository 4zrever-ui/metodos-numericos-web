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


def real_roots_from_sympy(f_sympy) -> list[float] | None:
    """Fuente única de verdad para "raíces reales" (usada por auto_params y por
    el generador de Excel). Resuelve con SymPy y verifica que cada solución sea
    real NUMÉRICAMENTE (parte imaginaria ≈ 0), lo que la hace robusta al
    'casus irreducibilis' (cúbicas con 3 raíces reales que SymPy expresa con
    radicales complejos y cuyo `.is_real` queda en None).

    Devuelve la lista de raíces reales (posiblemente []), o None si SymPy no
    puede resolver simbólicamente (p. ej. trascendentes como tan(x)-x).
    """
    try:
        sols = sp.solve(f_sympy, _x)
    except Exception:
        return None
    if not sols:
        return None
    reals: list[float] = []
    for s in sols:
        try:
            v = complex(s.evalf())
            if abs(v.imag) < 1e-9:
                reals.append(round(v.real, 10))
        except Exception:
            pass
    return reals


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
            if not (math.isfinite(fa) and math.isfinite(fb)):
                continue
            # Standard sign change
            if fa * fb < 0:
                pairs.append((xs[i], xs[i + 1]))
            # Root lands exactly on a grid point: fa=0 or fb=0.
            # Build a wider bracket so interval methods still get f(a)*f(b)<0.
            elif fa == 0.0 and i > 0:
                fa_prev = eval_f(eq, xs[i - 1])
                if math.isfinite(fa_prev) and fa_prev * fb < 0:
                    pairs.append((xs[i - 1], xs[i + 1]))
            elif fb == 0.0 and i + 2 < len(xs):
                fb_next = eval_f(eq, xs[i + 2])
                if math.isfinite(fb_next) and fa * fb_next < 0:
                    pairs.append((xs[i], xs[i + 2]))
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


def _choose_root_ref(roots: list[float]) -> float:
    """
    Política de selección de raíz de referencia.

    Regla: raíz positiva más pequeña (más cercana a cero, excluyendo 0 exacto).
    Si no hay positivas, la menos negativa (más cercana a cero).
    Si solo hay 0, devuelve 0.

    Esta función es la ÚNICA que implementa la política. Todo lo demás
    (x0, x0_alt, [a,b]) se deriva de su resultado, no al revés.

    Ejemplos:
        [-1.414, +1.414]        → +1.414
        [-1, +5]                → +5
        [-1, +100]              → +100   (única positiva, aunque sea grande)
        [-2.645, 0, +2.645]     → +2.645 (cero excluido de positivos)
        [-2, +2]                → +2
        [-5, -1]                → -1     (sin positivos, la menos negativa)
        [0]                     → 0
    """
    if not roots:
        return 1.0
    pos = [r for r in roots if r > 0]
    if pos:
        return min(pos, key=abs)          # positiva más cercana a cero
    zeros = [r for r in roots if r == 0]
    if zeros:
        return 0.0
    return max(roots)                     # sin positivos: la menos negativa


def _build_bracket_for(root: float, eq: ParsedEquation,
                        sign_changes: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Devuelve el mejor intervalo [a, b] con f(a)·f(b) < 0 que encierra `root`.

    Orden de preferencia:
    1. Intervalo de sign_changes cuyo midpoint está más cerca de root.
    2. Si ninguno encierra root (raíz fuera de la grilla ±15), construir un
       bracket sintético [root-δ, root+δ] verificado numéricamente, ampliando
       δ hasta encontrar un cambio de signo real.

    Nota: los métodos de intervalo (Bisección, Regula Falsi) usarán este [a,b].
    Si root está fuera de la grilla, el bracket sintético les permite converger
    a la misma raíz que los métodos de punto inicial.
    """
    # Deduplicate sign_changes
    seen: set = set()
    unique: list[tuple[float, float]] = []
    for pair in sign_changes:
        key = (round(pair[0], 8), round(pair[1], 8))
        if key not in seen:
            seen.add(key)
            unique.append(pair)

    if unique:
        # Sort by how close the midpoint is to root
        unique.sort(key=lambda p: abs((p[0] + p[1]) / 2 - root))
        best = unique[0]
        # Accept only if it actually brackets root (or is the best available)
        # — always take the closest one; if root is outside all brackets,
        # we fall through to the synthetic bracket below.
        mid = (best[0] + best[1]) / 2
        # If the closest bracket's midpoint is within 2 units of root, use it
        if abs(mid - root) <= max(2.0, abs(root) * 0.1):
            return best

    # Synthetic bracket: expand δ until we find a real sign change around root
    for delta in [0.5, 1.0, 2.0, 5.0, 10.0, abs(root) * 0.1 + 1.0]:
        a_try = root - delta
        b_try = root + delta
        try:
            fa = eval_f(eq, a_try)
            fb = eval_f(eq, b_try)
            if math.isfinite(fa) and math.isfinite(fb) and fa * fb < 0:
                return (a_try, b_try)
        except Exception:
            continue

    # Last resort: return a narrow window (interval methods may not converge,
    # but open methods will still use x0 derived from root independently)
    return (root - 0.5, root + 0.5)


def generate_params(eq: ParsedEquation) -> AutoParams:
    """
    Arquitectura de generación de parámetros automáticos.

    Flujo:
      1. Recolectar TODAS las raíces reales (SymPy primero, grilla como respaldo).
      2. Elegir root_ref con _choose_root_ref()  ← única fuente de verdad.
      3. Derivar [a,b], x0, x0_alt, g(x) TODOS desde root_ref.

    De esta forma, cuando una ecuación tiene raíces de ambos signos, todos los
    métodos (abiertos y cerrados) intentan converger a la misma raíz.
    """
    # ── Paso 1: recolectar raíces ──────────────────────────────────────────────

    # 1a. SymPy es la fuente principal (no tiene límite de ±15). Vía la fuente
    #     única real_roots_from_sympy, que verifica realidad NUMÉRICAMENTE
    #     (robusta al casus irreducibilis: x³−4x+1 con 3 raíces reales).
    roots_approx: list[float] = []
    sym_reals = real_roots_from_sympy(eq.f_sympy)
    if sym_reals:
        roots_approx = [r for r in sym_reals if math.isfinite(r)]

    # 1b. Grilla ±15 como respaldo (detecta raíces que SymPy no puede resolver,
    #     e.g. tan(x)-x, sin(x), funciones trascendentes en general).
    #     Se procesan TODOS los intervalos encontrados (no solo los primeros 4)
    #     para evitar que raíces positivas queden fuera cuando hay muchas raíces
    #     negativas antes en la grilla.
    grid_ints = list(range(-15, 16))
    grid_fine = [i * 0.5 for i in range(-30, 31)]
    grid = sorted(set(grid_ints + grid_fine))

    sign_changes_raw = _find_sign_changes(eq, grid)

    # Deduplicate sign_changes (exact-root fix may produce duplicates)
    seen_sc: set = set()
    sign_changes: list[tuple[float, float]] = []
    for pair in sign_changes_raw:
        key = (round(pair[0], 8), round(pair[1], 8))
        if key not in seen_sc:
            seen_sc.add(key)
            sign_changes.append(pair)

    f_sign_change_found = len(sign_changes) > 0

    for sc_a, sc_b in sign_changes:          # all unique brackets, not just [:4]
        approx = _bisect_approx(eq, sc_a, sc_b)
        approx_r = round(approx, 10)
        # Verify the candidate is a real root (|f(x)| small), not a
        # discontinuity / asymptote (e.g. tan(x) at x=π/2 has sign change
        # but f → ±∞, not 0). Use a generous threshold since we only have
        # 50 bisection steps.
        try:
            fval = abs(eval_f(eq, approx_r))
            if not math.isfinite(fval) or fval > 1.0:
                continue   # pseudo-root from discontinuity — skip
        except Exception:
            continue
        if not any(abs(approx_r - er) < 1e-6 for er in roots_approx):
            roots_approx.append(approx_r)

    # 1c. Último recurso: mínimo |f(x)| en la grilla — SOLO si realmente toca el
    #     eje (|f|≈0). Antes se reportaba el mínimo siempre, generando una raíz
    #     fantasma x≈0 para ecuaciones sin raíz real (p. ej. x²+1 → f(0)=1). (G2)
    if not roots_approx:
        vals = [(abs(eval_f(eq, v)), v) for v in grid if math.isfinite(eval_f(eq, v))]
        if vals:
            vals.sort()
            if vals[0][0] < 1e-6:
                roots_approx = [vals[0][1]]

    # ── Paso 2: elegir root_ref ────────────────────────────────────────────────
    root_ref = _choose_root_ref(roots_approx)

    # ── Paso 3: derivar todo desde root_ref ───────────────────────────────────
    a, b = _build_bracket_for(root_ref, eq, sign_changes)
    x0     = _best_integer_near(root_ref, eq=eq)
    x0_alt = _best_integer_near(root_ref, exclude=x0, eq=eq)

    # g(x) candidates
    gx_candidates = _generate_gx_candidates(eq, root_ref) if roots_approx else []

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
                fp_penalty = 5  # si f' falla, penalizar
        # Penalizar x0=0: muchos métodos dividen por x o f'(0)=0
        if c == 0:
            fp_penalty += 8
        # Penalizar si f(c) no es finito (rompe la matemática)
        if eq is not None:
            try:
                fval = eval_f(eq, float(c))
                if not math.isfinite(fval):
                    fp_penalty += 20
            except Exception:
                fp_penalty += 20
        return (fp_penalty, sign_prio, dist)

    candidates.sort(key=sort_key)
    return float(candidates[0]) if candidates else val