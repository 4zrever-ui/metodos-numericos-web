"""
test_newton_raphson.py
Batería completa para backend/methods/newton_raphson.py

Ecuación principal: x^3 - 4x + 1 = 0
  f'(x) = 3x^2 - 4
  f'(1)  = -1  (válido)
  f'(2)  =  8  (válido)
  f'(0) derivada = -4 (válido) — para inaplicabilidad usamos x^2-2 con f'(0)=0

Raíces reales conocidas: -2.114908, 0.254102, 1.860806
"""

from __future__ import annotations
import pytest

from backend.methods.newton_raphson import run
from backend.core.equation_parser import parse_equation


# ──────────────────────────────────────────────────────────────────────────────
# 1. Convergencia correcta
# ──────────────────────────────────────────────────────────────────────────────

class TestNewtonRaphsonConvergencia:

    def test_converge_raiz_positiva(self, eq_base, params_x0_valido):
        """x0=1 converge hacia raíz ~1.8608 de x^3-4x+1."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert result.applicable is True
        assert result.converged is True
        assert result.root is not None
        assert abs(result.root - 1.860806) < 1e-4

    def test_converge_raiz_pequena(self, eq_base, params_x0_valido):
        """x0=0 converge hacia raíz ~0.2541."""
        result = run(eq_base, params_x0_valido, x0=0.0)
        assert result.converged is True
        assert abs(result.root - 0.254102) < 1e-4

    def test_converge_raiz_negativa(self, eq_base, params_x0_negativo):
        """x0=-2 converge hacia raíz ~-2.1149."""
        result = run(eq_base, params_x0_negativo, x0=-2.0)
        assert result.converged is True
        assert abs(result.root - (-2.114908)) < 1e-4

    def test_convergencia_cuadratica_pocas_iteraciones(self, eq_base, params_x0_valido):
        """Newton-Raphson converge cuadráticamente: debe converger en < 10 iter."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert result.iteration_count < 10

    def test_raiz_exacta_entera(self, eq_raiz_entera, params_raiz_entera_intervalo):
        """f(x)=x^2-4: raíz exacta en x=2. x0=3 debe converger exactamente."""
        result = run(eq_raiz_entera, params_raiz_entera_intervalo, x0=3.0)
        assert result.converged is True
        assert abs(result.root - 2.0) < 1e-6

    def test_error_final_menor_tolerancia(self, eq_base, params_x0_valido):
        """El error% final debe ser menor que la tolerancia usada."""
        tol = 0.00001
        result = run(eq_base, params_x0_valido, x0=1.0, tol=tol)
        assert result.final_error_pct is not None
        assert result.final_error_pct < tol

    def test_result_fields_completos(self, eq_base, params_x0_valido):
        """MethodResult debe tener todos los campos obligatorios poblados."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert result.method_name == "Newton-Raphson"
        assert result.excel_sheet_name == "Newton-Raphson"
        assert result.formula_description != ""
        assert result.equation_str == eq_base.raw
        assert len(result.iterations) > 0

    def test_formula_description(self, eq_base, params_x0_valido):
        """La descripción de fórmula debe contener la notación de Newton."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert "f'" in result.formula_description or "f'(" in result.formula_description


# ──────────────────────────────────────────────────────────────────────────────
# 2. Inaplicabilidad
# ──────────────────────────────────────────────────────────────────────────────

class TestNewtonRaphsonInaplicable:

    def test_fp_cero_en_x0(self, eq_cuadratica, params_x0_derivada_cero):
        """RIESGO: f'(x0)=0 → división por cero en la fórmula xn+1 = xn - f/f'.
        Debe retornar applicable=False antes de iterar."""
        result = run(eq_cuadratica, params_x0_derivada_cero, x0=0.0)
        assert result.applicable is False
        assert result.converged is False
        assert result.iteration_count == 0
        assert len(result.iterations) == 0
        assert "0" in result.reason or "≈ 0" in result.reason

    def test_fp_casi_cero_en_iteracion(self, eq_base, params_x0_valido):
        """RIESGO: f'(xk)≈0 en una iteración intermedia causa break silencioso.
        El resultado debe ser no-convergente pero con root válido (última aproximación)."""
        # Construir ecuación donde f' cruza cero cerca de la raíz
        eq_especial = parse_equation("x^3 - 3*x")
        # f'(x) = 3x^2-3 = 0 en x=1, f(1)=-2. x0=1 → f'(1)=0 en primera iteración
        from backend.core.auto_params import AutoParams
        params_especial = AutoParams(
            a=0.0, b=2.0, x0=1.0, x0_alt=2.0, x0_von_mises=1.0,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[0.0, 1.732],
            f_sign_change_found=True,
        )
        result = run(eq_especial, params_especial, x0=1.0)
        # f'(1) = 0 → break interno, no convergencia
        assert result.root is not None  # siempre devuelve última aproximación

    def test_no_convergencia_max_iter(self, eq_base, params_no_convergencia):
        """Con max_iter=1 la mayoría de ecuaciones no convergen."""
        result = run(eq_base, params_no_convergencia, x0=1.0, max_iter=1)
        assert result.applicable is True
        assert (result.root is not None) == result.converged  # coherencia: root sólo si convergió

    def test_ecuacion_sin_raices_reales(self, eq_discriminante_negativo, params_discriminante_negativo):
        """f(x)=x^2+x+1 sin raíces reales. f'(0)=1≠0 → aplicable pero no converge."""
        result = run(eq_discriminante_negativo, params_discriminante_negativo, x0=0.0)
        assert result.applicable is True
        assert result.converged is False


# ──────────────────────────────────────────────────────────────────────────────
# 3. Estructura de iteraciones
# ──────────────────────────────────────────────────────────────────────────────

class TestNewtonRaphsonIteraciones:

    def test_primera_fila_tiene_k0(self, eq_base, params_x0_valido):
        """La primera fila de iteraciones debe ser k=0."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert result.iterations[0].k == 0

    def test_filas_tienen_fpxk_no_cero(self, eq_base, params_x0_valido):
        """Todas las filas deben tener fpxk ≠ 0 (de lo contrario hay break)."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        for row in result.iterations:
            assert abs(row.fpxk) > 1e-15

    def test_error_primera_fila_existe(self, eq_base, params_x0_valido):
        """La primera fila k=0 ya tiene error calculado (Newton calcula desde k=0)."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        # Newton calcula x_next en k=0, por lo que error_pct existe desde k=0
        assert result.iterations[0].error_pct is not None

    def test_error_decreciente(self, eq_base, params_x0_valido):
        """RIESGO (convergencia cuadrática): el error debe decrecer entre iteraciones."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        errors = [r.error_pct for r in result.iterations if r.error_pct is not None]
        if len(errors) >= 2:
            # Al menos el error final debe ser menor que el inicial
            assert errors[-1] < errors[0]

    def test_iteration_count_coincide_con_len(self, eq_base, params_x0_valido):
        """result.iteration_count debe ser len(iterations) - 1."""
        result = run(eq_base, params_x0_valido, x0=1.0)
        assert result.iteration_count == len(result.iterations) - 1

    def test_tolerancia_estricta_mas_iteraciones(self, eq_base, params_x0_valido):
        """Con tolerancia más estricta se necesitan más o igual iteraciones."""
        r_normal = run(eq_base, params_x0_valido, x0=1.0, tol=0.00001)
        r_estricto = run(eq_base, params_x0_valido, x0=1.0, tol=1e-10)
        assert r_estricto.iteration_count >= r_normal.iteration_count