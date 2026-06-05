"""
conftest.py — Fixtures compartidas para todos los tests de métodos numéricos.

Ecuación de referencia principal: f(x) = x^3 - 4x + 1
  Raíces reales: -2.114908, 0.254102, 1.860806
  Cambio de signo: [0,1] y [1,2] y [-3,-2]
  Sin cambio de signo: [2,3]

Ecuación auxiliar (derivada cero): f(x) = x^2 - 2
  f'(0) = 0  → útil para test de inaplicabilidad en Newton/VonMises

Todas las fixtures están diseñadas para ser deterministas y sin dependencia
de generate_params(), de modo que los tests sean predecibles y rápidos.
"""

from __future__ import annotations
import pytest
import sympy as sp

from backend.core.equation_parser import parse_equation, ParsedEquation
from backend.core.auto_params import AutoParams

_x = sp.Symbol("x")

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_params(
    a=0.0, b=1.0,
    x0=1.0, x0_alt=2.0,
    x0_von_mises=1.0,
    tol=0.00001, max_iter=25,
    gx_sympy=None,
    gx_excel="", gx_latex="",
) -> AutoParams:
    """Construye un AutoParams mínimo para tests (sin ejecutar generate_params)."""
    return AutoParams(
        a=a, b=b,
        x0=x0, x0_alt=x0_alt,
        x0_von_mises=x0_von_mises,
        tol=tol, max_iter=max_iter,
        gx_sympy=gx_sympy,
        gx_excel=gx_excel,
        gx_latex=gx_latex,
        gx_candidates=[],
        roots_approx=[0.254102, 1.860806, -2.114908],
        f_sign_change_found=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Ecuaciones parseadas
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def eq_base() -> ParsedEquation:
    """f(x) = x^3 - 4x + 1. Ecuación de referencia principal."""
    return parse_equation("x^3 - 4*x + 1")


@pytest.fixture(scope="session")
def eq_cuadratica() -> ParsedEquation:
    """f(x) = x^2 - 2. Raíz = sqrt(2). f'(0) = 0 (útil para test de inaplicabilidad)."""
    return parse_equation("x^2 - 2")


@pytest.fixture(scope="session")
def eq_simple() -> ParsedEquation:
    """f(x) = x^3 - x - 1. Una sola raíz real ~1.3247. Sin raíz entera."""
    return parse_equation("x^3 - x - 1")


@pytest.fixture(scope="session")
def eq_raiz_entera() -> ParsedEquation:
    """f(x) = x^2 - 4. Raíces exactas en x=2 y x=-2."""
    return parse_equation("x^2 - 4")


# ──────────────────────────────────────────────────────────────────────────────
# Parámetros para métodos de intervalo (Bisección, Regula Falsi)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def params_intervalo_valido(eq_base) -> AutoParams:
    """Intervalo [0,1] con cambio de signo confirmado para x^3-4x+1.
    f(0)=1 > 0,  f(1)=-2 < 0."""
    return _make_params(a=0.0, b=1.0, x0=1.0, x0_alt=2.0)


@pytest.fixture(scope="session")
def params_intervalo_alterno(eq_base) -> AutoParams:
    """Intervalo [1,2] con cambio de signo confirmado.
    f(1)=-2 < 0,  f(2)=1 > 0."""
    return _make_params(a=1.0, b=2.0, x0=1.0, x0_alt=2.0)


@pytest.fixture(scope="session")
def params_sin_cambio_signo(eq_base) -> AutoParams:
    """Intervalo [2,3] sin cambio de signo: f(2)=1, f(3)=16.
    → Bisección y Regula Falsi deben retornar applicable=False."""
    return _make_params(a=2.0, b=3.0, x0=2.0, x0_alt=3.0)


@pytest.fixture(scope="session")
def params_intervalo_negativo(eq_base) -> AutoParams:
    """Intervalo [-3,-2] con cambio de signo. f(-3)=-14, f(-2)=1."""
    return _make_params(a=-3.0, b=-2.0, x0=-2.0, x0_alt=-3.0)


@pytest.fixture(scope="session")
def params_raiz_entera_intervalo(eq_raiz_entera) -> AutoParams:
    """Intervalo [1,3] para x^2-4=0. Raíz exacta en x=2."""
    return _make_params(a=1.0, b=3.0, x0=1.0, x0_alt=3.0)


# ──────────────────────────────────────────────────────────────────────────────
# Parámetros para métodos de punto único (Newton, Von Mises, Secante)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def params_x0_valido(eq_base) -> AutoParams:
    """x0=1 para x^3-4x+1. f'(1) = 3(1)^2-4 = -1 ≠ 0. Convergencia garantizada."""
    return _make_params(x0=1.0, x0_alt=2.0, x0_von_mises=1.0)


@pytest.fixture(scope="session")
def params_x0_derivada_cero(eq_cuadratica) -> AutoParams:
    """x0=0 para x^2-2. f'(0) = 2*0 = 0.
    → Newton-Raphson y Von Mises deben retornar applicable=False."""
    return _make_params(x0=0.0, x0_alt=1.0, x0_von_mises=0.0)


@pytest.fixture(scope="session")
def params_secante_valido(eq_base) -> AutoParams:
    """x0=1, x1=2 para Secante sobre x^3-4x+1."""
    return _make_params(x0=1.0, x0_alt=2.0)


@pytest.fixture(scope="session")
def params_secante_mismo_punto(eq_base) -> AutoParams:
    """x0=x1=1: denom = f(x1)-f(x0) = 0 en el primer paso."""
    return _make_params(x0=1.0, x0_alt=1.0)


@pytest.fixture(scope="session")
def params_x0_negativo(eq_base) -> AutoParams:
    """x0=-2 para x^3-4x+1. f'(-2) = 3(4)-4 = 8 ≠ 0.
    Converge hacia raíz negativa ~-2.1149."""
    return _make_params(x0=-2.0, x0_alt=-3.0, x0_von_mises=-2.0)


@pytest.fixture(scope="session")
def params_no_convergencia(eq_base) -> AutoParams:
    """max_iter=1 para forzar no-convergencia en cualquier método."""
    return _make_params(x0=1.0, x0_alt=2.0, a=0.0, b=1.0, max_iter=1)


# ──────────────────────────────────────────────────────────────────────────────
# Parámetros con g(x) para Punto Fijo, Aitken, Steffensen
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def params_gx_convergente(eq_base) -> AutoParams:
    """g(x) = (x^3 + 1) / 4 para x^3-4x+1=0.
    |g'(0.254102)| ≈ 0.0484 < 1. Converge localmente hacia x ≈ 0.254102."""
    gx = (_x**3 + 1) / 4
    return _make_params(
        x0=0.0, x0_alt=1.0,
        gx_sympy=gx,
        gx_latex=r"\frac{x^{3}+1}{4}",
        gx_excel="=({col}{row}^3+1)/4",
    )


@pytest.fixture(scope="session")
def params_gx_divergente() -> AutoParams:
    """g(x) = x^3 + x. |g'(1)| = 4 > 1. Diverge siempre."""
    gx = _x**3 + _x
    return _make_params(
        x0=1.0, x0_alt=2.0,
        gx_sympy=gx,
        gx_latex="x^{3}+x",
        gx_excel="={col}{row}^3+{col}{row}",
    )


@pytest.fixture(scope="session")
def params_gx_none() -> AutoParams:
    """gx_sympy=None: Punto Fijo, Aitken y Steffensen deben retornar applicable=False."""
    return _make_params(x0=1.0, x0_alt=2.0, gx_sympy=None)


@pytest.fixture(scope="session")
def params_tolerancia_laxa(eq_base) -> AutoParams:
    """Tolerancia muy laxa (1.0 = 100%). Converge en 1 iteración."""
    gx = (_x**3 + 1) / 4
    return _make_params(
        a=0.0, b=1.0, x0=0.0, x0_alt=1.0,
        tol=1.0,
        gx_sympy=gx,
    )


@pytest.fixture(scope="session")
def params_tolerancia_estricta(eq_base) -> AutoParams:
    """Tolerancia muy estricta (1e-10). Requiere más iteraciones."""
    gx = (_x**3 + 1) / 4
    return _make_params(
        a=0.0, b=1.0, x0=0.0, x0_alt=1.0,
        tol=1e-10,
        gx_sympy=gx,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Parámetros para Newton Family (variantes de orden superior)
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def params_newton_family_valido(eq_base) -> AutoParams:
    """x0=1 para todas las variantes de newton_family sobre x^3-4x+1.
    f'(1)=-1 ≠ 0, f''(1)=6."""
    return _make_params(x0=1.0, x0_alt=2.0)


@pytest.fixture(scope="session")
def params_newton_family_fp_cero(eq_cuadratica) -> AutoParams:
    """x0=0 para x^2-2: f'(0)=0 → todas las variantes inaplicables."""
    return _make_params(x0=0.0, x0_alt=1.0)


@pytest.fixture(scope="session")
def eq_discriminante_negativo() -> ParsedEquation:
    """f(x) = x^2 + x + 1. Sin raíces reales.
    Newton 2do Orden: discriminante = (f')^2 - 2*f''*f puede ser negativo."""
    return parse_equation("x^2 + x + 1")


@pytest.fixture(scope="session")
def params_discriminante_negativo(eq_discriminante_negativo) -> AutoParams:
    """x0=0 para x^2+x+1. f'(0)=1 ≠ 0, f''=2, discriminante=1-2*1=-1 < 0."""
    return _make_params(x0=0.0, x0_alt=1.0)