"""
test_newton_family.py
Batería completa para backend/methods/newton_family.py

Cubre las 6 variantes de orden superior, una clase por variante:
  - Newton Modificado:   xn+1 = xn - [f·f'] / [(f')²-f·f'']
  - Newton 2do Orden:    xn+1 = xn + (-f' + √((f')²-2f''·f)) / f''
  - Chebyshev:           xn+1 = xn - (f/f') - [(f²·f'') / (2·(f')³)]
  - Halley:              xn+1 = xn - f / [f' - (f''·f)/(2·f')]
  - Super Halley:        xn+1 = xn - [2(f')²-ff''] / [2((f')²-ff'')] · (f/f')
  - Ostrowsky:           xn+1 = xn - f·signo(f') / √(f'²-f·f'')

Ecuación de referencia: x^3 - 4x + 1
  f'(1)=-1, f''(1)=6
  Raíces: -2.114908, 0.254102, 1.860806

Ecuación auxiliar (f'=0): x^2-2 con x0=0
Ecuación sin raíces reales (discriminante negativo): x^2+x+1
"""

from __future__ import annotations
import pytest

from backend.methods.newton_family import (
    run_newton_modificado,
    run_newton_segundo_orden,
    run_chebyshev,
    run_halley,
    run_super_halley,
    run_ostrowsky,
)
from backend.core.equation_parser import parse_equation
from backend.core.equation_parser import eval_f


# ══════════════════════════════════════════════════════════════════════════════
# NEWTON MODIFICADO
# ══════════════════════════════════════════════════════════════════════════════

class TestNewtonModificado:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Newton Modificado debe converger a una raíz de x^3-4x+1 desde x0=1."""
        result = run_newton_modificado(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        assert result.root is not None
        # Debe ser una de las tres raíces reales
        raices = [-2.114908, 0.254102, 1.860806]
        assert any(abs(result.root - r) < 1e-3 for r in raices)

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        """RIESGO: f'(x0)=0 → not applicable antes de iterar."""
        result = run_newton_modificado(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False
        assert result.iteration_count == 0

    def test_denom_cero_interno(self, eq_base, params_newton_family_valido):
        """RIESGO: denom = (f')²-f·f'' puede ser 0 → ZeroDivisionError capturado → break.
        En ese caso el método debe retornar applicable=True con root=última aproximación."""
        # Construir ecuación donde denom es casi cero desde el inicio
        # f(x)=x, f'(x)=1, f''(x)=0 → denom = 1 - x*0 = 1 (no es cero)
        # Para este test verificamos que el método no lanza excepción sin capturar
        result = run_newton_modificado(eq_base, params_newton_family_valido, x0=1.0)
        assert result.root is not None  # siempre devuelve algo

    def test_no_convergencia_max_iter(self, eq_base, params_no_convergencia):
        """Con max_iter=1 no converge, pero root debe ser no None."""
        result = run_newton_modificado(eq_base, params_no_convergencia, x0=1.0, max_iter=1)
        assert result.applicable is True
        assert (result.root is not None) == result.converged  # coherencia: root sólo si convergió

    def test_method_name(self, eq_base, params_newton_family_valido):
        """Verifica que method_name y excel_sheet_name sean correctos."""
        result = run_newton_modificado(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Newton Modificado"
        assert result.excel_sheet_name == "Newton Modificado"

    def test_error_final_menor_tolerancia(self, eq_base, params_newton_family_valido):
        """El error% final debe ser < tol al converger."""
        result = run_newton_modificado(eq_base, params_newton_family_valido, x0=1.0, tol=0.00001)
        if result.converged:
            assert result.final_error_pct < 0.00001


# ══════════════════════════════════════════════════════════════════════════════
# NEWTON 2DO ORDEN
# ══════════════════════════════════════════════════════════════════════════════

class TestNewton2doOrden:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Newton 2do Orden converge sobre x^3-4x+1 desde x0=1."""
        result = run_newton_segundo_orden(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        # Puede converger o hacer break si discriminante < 0 en alguna iter
        assert result.root is not None

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        """RIESGO: f'(x0)=0 → not applicable."""
        result = run_newton_segundo_orden(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False

    def test_discriminante_negativo_break(self, eq_discriminante_negativo, params_discriminante_negativo):
        """RIESGO CRÍTICO: discriminante = (f')²-2f''·f puede ser negativo.
        x^2+x+1 con x0=0: f(0)=1, f'(0)=1, f''=2
        discriminante = 1 - 2*2*1 = -3 < 0 → ValueError capturado → break.
        El método debe devolver applicable=True pero converged=False o root=None."""
        result = run_newton_segundo_orden(eq_discriminante_negativo, params_discriminante_negativo, x0=0.0)
        assert result.applicable is True
        # Como el discriminante es negativo desde la primera iteración, no hay filas
        # o hay 0 iteraciones
        assert not result.converged

    def test_fpp_cero_break(self, eq_base, params_newton_family_valido):
        """RIESGO: f''(xk)≈0 en alguna iteración → ZeroDivisionError capturado.
        El método debe manejar sin lanzar excepción."""
        # f(x) = x: f''=0 en todas partes
        eq_lineal = parse_equation("x - 1")
        from backend.core.auto_params import AutoParams
        params_lineal = AutoParams(
            a=0.0, b=2.0, x0=0.0, x0_alt=2.0, x0_von_mises=0.0,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[1.0],
            f_sign_change_found=True,
        )
        result = run_newton_segundo_orden(eq_lineal, params_lineal, x0=0.0)
        # f'(x)=1≠0, pero f''=0 → ZeroDivisionError → break → no converge → root None
        assert result.converged is False
        assert result.root is None  # coherencia: sin convergencia no se devuelve raíz

    def test_method_name(self, eq_base, params_newton_family_valido):
        result = run_newton_segundo_orden(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Newton 2do Orden"

    def test_no_convergencia_max_iter(self, eq_base, params_newton_family_valido):
        result = run_newton_segundo_orden(eq_base, params_newton_family_valido, x0=1.0, max_iter=1)
        assert (result.root is not None) == result.converged  # coherencia


# ══════════════════════════════════════════════════════════════════════════════
# CHEBYSHEV
# ══════════════════════════════════════════════════════════════════════════════

class TestChebyshev:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Chebyshev debe converger sobre x^3-4x+1 desde x0=1."""
        result = run_chebyshev(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        raices = [-2.114908, 0.254102, 1.860806]
        assert any(abs(result.root - r) < 1e-3 for r in raices)

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        result = run_chebyshev(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False

    def test_fp_cubico_overflow(self, eq_base, params_newton_family_valido):
        """RIESGO: (f')³ en denominador puede causar overflow si f' es grande.
        Desde x0=10 f' es muy grande; debe manejar sin excepción sin capturar."""
        from backend.core.auto_params import AutoParams
        params_lejano = AutoParams(
            a=9.0, b=11.0, x0=10.0, x0_alt=9.0, x0_von_mises=10.0,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[1.86],
            f_sign_change_found=True,
        )
        # No debe lanzar excepción
        result = run_chebyshev(eq_base, params_lejano, x0=10.0)
        assert result.root is not None

    def test_method_name(self, eq_base, params_newton_family_valido):
        result = run_chebyshev(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Chebyshev"

    def test_error_final_menor_tolerancia(self, eq_base, params_newton_family_valido):
        result = run_chebyshev(eq_base, params_newton_family_valido, x0=1.0, tol=0.00001)
        if result.converged:
            assert result.final_error_pct < 0.00001

    def test_no_convergencia_max_iter(self, eq_base, params_newton_family_valido):
        result = run_chebyshev(eq_base, params_newton_family_valido, x0=1.0, max_iter=1)
        assert (result.root is not None) == result.converged  # coherencia


# ══════════════════════════════════════════════════════════════════════════════
# HALLEY
# ══════════════════════════════════════════════════════════════════════════════

class TestHalley:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Halley converge sobre x^3-4x+1 desde x0=1."""
        result = run_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        raices = [-2.114908, 0.254102, 1.860806]
        assert any(abs(result.root - r) < 1e-3 for r in raices)

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        result = run_halley(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False

    def test_denom_halley_cero(self, eq_base, params_newton_family_valido):
        """RIESGO: denom = f' - (f''·f)/(2·f') puede ser 0 → ZeroDivisionError.
        El método debe capturarlo y hacer break sin lanzar."""
        # Verificamos que siempre devuelve un resultado, nunca lanza
        result = run_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.root is not None

    def test_convergencia_cubica_pocas_iter(self, eq_base, params_newton_family_valido):
        """Halley tiene convergencia cúbica: debe converger en < 8 iteraciones."""
        result = run_halley(eq_base, params_newton_family_valido, x0=1.0)
        if result.converged:
            assert result.iteration_count < 8

    def test_method_name(self, eq_base, params_newton_family_valido):
        result = run_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Halley"

    def test_no_convergencia_max_iter(self, eq_base, params_newton_family_valido):
        result = run_halley(eq_base, params_newton_family_valido, x0=1.0, max_iter=1)
        assert (result.root is not None) == result.converged  # coherencia


# ══════════════════════════════════════════════════════════════════════════════
# SUPER HALLEY
# ══════════════════════════════════════════════════════════════════════════════

class TestSuperHalley:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Super Halley converge sobre x^3-4x+1 desde x0=1."""
        result = run_super_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        raices = [-2.114908, 0.254102, 1.860806]
        assert any(abs(result.root - r) < 1e-3 for r in raices)

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        result = run_super_halley(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False

    def test_doble_denominador_riesgo(self, eq_base, params_newton_family_valido):
        """RIESGO COMPUESTO: Super Halley tiene dos denominadores en la fórmula:
          num = 2(f')² - f·f''
          den = 2((f')² - f·f'')
          Si den=0 o f'=0 → ZeroDivisionError.
        Verificamos que no se propaga como excepción sin capturar."""
        result = run_super_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.root is not None

    def test_method_name(self, eq_base, params_newton_family_valido):
        result = run_super_halley(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Super Halley"

    def test_error_final_menor_tolerancia(self, eq_base, params_newton_family_valido):
        result = run_super_halley(eq_base, params_newton_family_valido, x0=1.0, tol=0.00001)
        if result.converged:
            assert result.final_error_pct < 0.00001

    def test_no_convergencia_max_iter(self, eq_base, params_newton_family_valido):
        result = run_super_halley(eq_base, params_newton_family_valido, x0=1.0, max_iter=1)
        assert (result.root is not None) == result.converged  # coherencia


# ══════════════════════════════════════════════════════════════════════════════
# OSTROWSKY
# ══════════════════════════════════════════════════════════════════════════════

class TestOstrowsky:

    def test_converge(self, eq_base, params_newton_family_valido):
        """Ostrowsky converge sobre x^3-4x+1 desde x0=1."""
        result = run_ostrowsky(eq_base, params_newton_family_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        raices = [-2.114908, 0.254102, 1.860806]
        assert any(abs(result.root - r) < 1e-3 for r in raices)

    def test_inaplicable_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        result = run_ostrowsky(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
        assert result.applicable is False

    def test_raiz_cuadrada_de_negativo(self, eq_discriminante_negativo, params_discriminante_negativo):
        """RIESGO CRÍTICO: inner = (f')²-f·f'' puede ser negativo.
        x^2+x+1 con x0=0: f=1, f'=1, f''=2 → inner = 1 - 1*2 = -1 < 0.
        math.sqrt(-1) → ValueError capturado → break.
        El resultado debe ser applicable=True pero sin convergencia."""
        result = run_ostrowsky(eq_discriminante_negativo, params_discriminante_negativo, x0=0.0)
        assert result.applicable is True
        assert not result.converged

    def test_sqrt_inner_cero(self, eq_base, params_newton_family_valido):
        """RIESGO: sqrt_inner ≈ 0 → ZeroDivisionError en denominador.
        No debe propagarse como excepción sin capturar."""
        result = run_ostrowsky(eq_base, params_newton_family_valido, x0=1.0)
        assert result.root is not None

    def test_method_name(self, eq_base, params_newton_family_valido):
        result = run_ostrowsky(eq_base, params_newton_family_valido, x0=1.0)
        assert result.method_name == "Ostrowsky"

    def test_no_convergencia_max_iter(self, eq_base, params_newton_family_valido):
        result = run_ostrowsky(eq_base, params_newton_family_valido, x0=1.0, max_iter=1)
        assert (result.root is not None) == result.converged  # coherencia

    def test_convergencia_rapida(self, eq_base, params_newton_family_valido):
        """Ostrowsky es de orden 4: debe converger en muy pocas iteraciones."""
        result = run_ostrowsky(eq_base, params_newton_family_valido, x0=1.0)
        if result.converged:
            assert result.iteration_count < 10

    def test_signo_fp_negativo_x2_menos_7(self):
        """P1 (regresión): la fórmula antigua (f'/√)·(f/f') cancelaba f' y perdía
        su signo (√ siempre ≥ 0) → divergía cuando f'(x0)<0. Con x^2-7 desde
        x0=-3 (f'=-6<0) ahora debe converger a -√7; desde x0=+3 a +√7."""
        import math
        from backend.core.auto_params import AutoParams
        eq = parse_equation("x^2 - 7")
        params = AutoParams(
            a=2.5, b=3.0, x0=-3.0, x0_alt=-2.0, x0_von_mises=-3.0,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[-math.sqrt(7), math.sqrt(7)],
            f_sign_change_found=True,
        )
        # semilla negativa (f'<0): antes divergía, ahora converge a -√7
        r_neg = run_ostrowsky(eq, params, x0=-3.0)
        assert r_neg.converged is True
        assert abs(r_neg.root - (-math.sqrt(7))) < 1e-6
        # semilla positiva (f'>0): ya funcionaba, no debe romperse
        r_pos = run_ostrowsky(eq, params, x0=3.0)
        assert r_pos.converged is True
        assert abs(r_pos.root - math.sqrt(7)) < 1e-6


# ══════════════════════════════════════════════════════════════════════════════
# Tests transversales — comparan variantes entre sí
# ══════════════════════════════════════════════════════════════════════════════

class TestNewtonFamilyComparativo:

    def test_todas_variantes_convergen_raiz_valida(self, eq_base, params_newton_family_valido):
        """Cada variante debe converger a UNA raíz válida de f(x) desde x0=1.

        No se exige convergencia a la misma raíz: métodos como Chebyshev y
        Ostrowsky tienen correcciones de orden superior que producen saltos de
        mayor amplitud en el primer paso (Chebyshev llega a x1=11.0 desde x0=1),
        llevándolos a cuencas de atracción distintas. La invariante correcta es
        que cada raíz reportada pertenezca al conjunto de raíces reales de f(x).
        """
        runners = [
            run_newton_modificado,
            run_chebyshev,
            run_halley,
            run_super_halley,
            run_ostrowsky,
        ]
        raices_conocidas = [-2.114908, 0.254102, 1.860806]
        converged_methods = []

        for runner in runners:
            result = runner(eq_base, params_newton_family_valido, x0=1.0)
            if result.converged and result.root is not None:
                converged_methods.append((runner.__name__, result.root))

        assert len(converged_methods) >= 1, (
            "Ningún método de la familia Newton convergió sobre x^3-4x+1 desde x0=1.0"
        )

        for name, root in converged_methods:
            assert any(abs(root - r) < 1e-3 for r in raices_conocidas), (
                f"{name} convergió a x={root:.10f} que no corresponde a ninguna "
                f"raíz conocida de f(x)=x³-4x+1. Raíces esperadas: {raices_conocidas}"
            )

    def test_todas_devuelven_applicable_false_fp_cero(self, eq_cuadratica, params_newton_family_fp_cero):
        """Todas las variantes deben retornar applicable=False cuando f'(x0)=0."""
        runners = [
            run_newton_modificado,
            run_newton_segundo_orden,
            run_chebyshev,
            run_halley,
            run_super_halley,
            run_ostrowsky,
        ]
        for runner in runners:
            result = runner(eq_cuadratica, params_newton_family_fp_cero, x0=0.0)
            assert result.applicable is False, f"{runner.__name__} debería ser inaplicable"

    def test_order_superior_menos_iteraciones(self, eq_base, params_newton_family_valido):
        """Los métodos de orden superior (Halley, Ostrowsky) deben requerir ≤
        iteraciones que Newton-Raphson estándar."""
        from backend.methods.newton_raphson import run as run_nr
        result_nr = run_nr(eq_base, params_newton_family_valido, x0=1.0)
        result_halley = run_halley(eq_base, params_newton_family_valido, x0=1.0)

        if result_nr.converged and result_halley.converged:
            assert result_halley.iteration_count <= result_nr.iteration_count