"""
test_biseccion.py
Batería completa para backend/methods/biseccion.py

Método de Bisección:
  c = (a + b) / 2
  Actualiza [a, b] según el signo de fa·fc:
    fa·fc < 0 → b = c
    fa·fc ≥ 0 → a = c

Ecuación de referencia: x^3 - 4x + 1 = 0
  f(0) = 1  > 0,  f(1) = -2 < 0   → cambio de signo en [0, 1]  → raíz ≈ 0.254102
  f(1) = -2 < 0,  f(2) =  1 > 0   → cambio de signo en [1, 2]  → raíz ≈ 1.860806
  f(-3)= -14< 0,  f(-2)=  1 > 0   → cambio de signo en [-3,-2] → raíz ≈ -2.114908
  f(2) =  1 > 0,  f(3) = 16 > 0   → sin cambio de signo

Riesgos matemáticos cubiertos:
  - fa*fb > 0 → not applicable (Bolzano no aplica)
  - f(x) no finita en extremo → not applicable
  - max_iter=1 → no converge pero root es última aproximación
  - error_pct=None en k=0 (no hay punto previo)
  - c siempre en (a, b)
"""

from __future__ import annotations
import pytest

from backend.methods.biseccion import run
from backend.core.equation_parser import parse_equation
from backend.core.auto_params import AutoParams


# ──────────────────────────────────────────────────────────────────────────────
# 1. Convergencia correcta
# ──────────────────────────────────────────────────────────────────────────────

class TestBiseccionConvergencia:

    def test_converge_intervalo_0_1(self, eq_base, params_intervalo_valido):
        """Intervalo [0, 1] con cambio de signo: converge a raíz ~0.254102."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.applicable is True
        assert result.converged is True
        assert result.root is not None
        assert abs(result.root - 0.254102) < 1e-4

    def test_converge_intervalo_1_2(self, eq_base, params_intervalo_alterno):
        """Intervalo [1, 2]: converge a raíz ~1.860806."""
        result = run(eq_base, params_intervalo_alterno, a=1.0, b=2.0)
        assert result.applicable is True
        assert result.converged is True
        assert abs(result.root - 1.860806) < 1e-4

    def test_converge_intervalo_negativo(self, eq_base, params_intervalo_negativo):
        """Intervalo [-3, -2]: converge a raíz ~-2.114908."""
        result = run(eq_base, params_intervalo_negativo, a=-3.0, b=-2.0)
        assert result.applicable is True
        assert result.converged is True
        assert abs(result.root - (-2.114908)) < 1e-4

    def test_raiz_entera_exacta(self, eq_raiz_entera, params_raiz_entera_intervalo):
        """f(x)=x^2-4 con [1, 3]: raíz exacta en x=2."""
        result = run(eq_raiz_entera, params_raiz_entera_intervalo, a=1.0, b=3.0)
        assert result.applicable is True
        assert result.converged is True
        assert abs(result.root - 2.0) < 1e-4

    def test_error_final_menor_tolerancia(self, eq_base, params_intervalo_valido):
        """El error% final debe ser menor que la tolerancia usada."""
        tol = 0.00001
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0, tol=tol)
        if result.converged:
            assert result.final_error_pct is not None
            assert result.final_error_pct < tol

    def test_method_name_y_sheet(self, eq_base, params_intervalo_valido):
        """method_name y excel_sheet_name deben ser exactos."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.method_name == "Bisección"
        assert result.excel_sheet_name == "Bisección"

    def test_formula_description_contiene_formula(self, eq_base, params_intervalo_valido):
        """La descripción de fórmula debe contener la notación de punto medio."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert "c" in result.formula_description or "a" in result.formula_description

    def test_tolerancia_estricta_mas_iteraciones(self, eq_base, params_intervalo_valido):
        """Con tolerancia más estricta se necesitan más o igual iteraciones."""
        r_normal = run(eq_base, params_intervalo_valido, a=0.0, b=1.0, tol=0.00001)
        r_estricto = run(eq_base, params_intervalo_valido, a=0.0, b=1.0, tol=1e-10)
        assert r_estricto.iteration_count >= r_normal.iteration_count


# ──────────────────────────────────────────────────────────────────────────────
# 2. Inaplicabilidad
# ──────────────────────────────────────────────────────────────────────────────

class TestBiseccionInaplicable:

    def test_sin_cambio_signo(self, eq_base, params_sin_cambio_signo):
        """RIESGO: [2, 3] sin cambio de signo → not applicable."""
        result = run(eq_base, params_sin_cambio_signo, a=2.0, b=3.0)
        assert result.applicable is False
        assert result.converged is False
        assert result.root is None
        assert len(result.iterations) == 0

    def test_reason_explica_sin_cambio(self, eq_base, params_sin_cambio_signo):
        """El reason debe mencionar la ausencia de cambio de signo o Bolzano."""
        result = run(eq_base, params_sin_cambio_signo, a=2.0, b=3.0)
        reason_lower = result.reason.lower()
        assert (
            "signo" in reason_lower
            or "bolzano" in reason_lower
            or "sign" in reason_lower
        )

    def test_mismo_signo_positivo(self, eq_base):
        """fa y fb ambos positivos → not applicable."""
        params = AutoParams(
            a=2.0, b=4.0, x0=3.0, x0_alt=2.0, x0_von_mises=3.0,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[],
            f_sign_change_found=False,
        )
        result = run(eq_base, params, a=2.0, b=4.0)
        assert result.applicable is False

    def test_f_no_finita_en_extremo(self):
        """RIESGO: f(x) no finita en extremo del intervalo → not applicable."""
        eq_sing = parse_equation("1/x")
        params = AutoParams(
            a=-1.0, b=1.0, x0=0.5, x0_alt=1.0, x0_von_mises=0.5,
            tol=0.00001, max_iter=25,
            gx_sympy=None, gx_excel="", gx_latex="",
            gx_candidates=[], roots_approx=[],
            f_sign_change_found=False,
        )
        result = run(eq_sing, params, a=-1.0, b=1.0)
        assert result.applicable is False

    def test_no_convergencia_max_iter_1(self, eq_base, params_no_convergencia):
        """Con max_iter=1 no converge → root queda None (coherencia front/back/Excel)."""
        result = run(eq_base, params_no_convergencia, a=0.0, b=1.0, max_iter=1)
        assert result.applicable is True
        assert (result.root is not None) == result.converged

    def test_iteration_count_cero_si_inaplicable(self, eq_base, params_sin_cambio_signo):
        """Si not applicable, iteration_count debe ser 0."""
        result = run(eq_base, params_sin_cambio_signo, a=2.0, b=3.0)
        assert result.iteration_count == 0


# ──────────────────────────────────────────────────────────────────────────────
# 3. Estructura de MethodResult
# ──────────────────────────────────────────────────────────────────────────────

class TestBiseccionEstructura:

    def test_primera_fila_k0(self, eq_base, params_intervalo_valido):
        """La primera fila de iteraciones debe ser k=0."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.iterations[0].k == 0

    def test_primera_fila_sin_error(self, eq_base, params_intervalo_valido):
        """En k=0 no hay iteración previa → error_pct debe ser None."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.iterations[0].error_pct is None

    def test_primera_fila_converged_none(self, eq_base, params_intervalo_valido):
        """En k=0 no hay error calculado → converged debe ser None."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.iterations[0].converged is None

    def test_filas_tienen_fa_fc_fb(self, eq_base, params_intervalo_valido):
        """Cada IntervalRow debe tener fa, fc, fb poblados."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        for row in result.iterations:
            assert hasattr(row, "fa")
            assert hasattr(row, "fc")
            assert hasattr(row, "fb")

    def test_filas_tienen_fa_fc_product(self, eq_base, params_intervalo_valido):
        """Cada fila debe tener fa_fc poblado y coincidir con fa*fc."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        for row in result.iterations:
            assert hasattr(row, "fa_fc")
            assert abs(row.fa_fc - row.fa * row.fc) < 1e-12

    def test_iteration_count_len_minus_1(self, eq_base, params_intervalo_valido):
        """result.iteration_count debe ser len(iterations) - 1."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.iteration_count == len(result.iterations) - 1

    def test_params_usados_contienen_ab(self, eq_base, params_intervalo_valido):
        """params_used debe contener a, b y la ecuación."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert "a" in result.params_used
        assert "b" in result.params_used
        assert result.params_used["a"] == 0.0
        assert result.params_used["b"] == 1.0

    def test_equation_str_coincide(self, eq_base, params_intervalo_valido):
        """equation_str debe coincidir con el raw de la ecuación parseada."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.equation_str == eq_base.raw

    def test_latex_fields_poblados(self, eq_base, params_intervalo_valido):
        """f_latex, fp_latex y fpp_latex deben estar presentes."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert result.f_latex != ""
        assert result.fp_latex != ""
        assert result.fpp_latex != ""


# ──────────────────────────────────────────────────────────────────────────────
# 4. Tabla de iteraciones — valores numéricos
# ──────────────────────────────────────────────────────────────────────────────

class TestBiseccionTabla:

    def test_c_es_punto_medio(self, eq_base, params_intervalo_valido):
        """En cada fila, c debe ser exactamente (a + b) / 2."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        for row in result.iterations:
            assert abs(row.c - (row.a + row.b) / 2) < 1e-14

    def test_c_dentro_de_ab(self, eq_base, params_intervalo_valido):
        """c siempre debe estar dentro del intervalo (a, b)."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        for row in result.iterations:
            assert row.a <= row.c <= row.b

    def test_fa_evaluado_correctamente(self, eq_base, params_intervalo_valido):
        """fa en k=0 debe ser f(a_original)."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        from backend.core.equation_parser import eval_f
        fa_esperado = eval_f(eq_base, 0.0)
        assert abs(result.iterations[0].fa - fa_esperado) < 1e-12

    def test_fc_evaluado_en_c(self, eq_base, params_intervalo_valido):
        """fc en cada fila debe ser f(c)."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        from backend.core.equation_parser import eval_f
        for row in result.iterations:
            fc_esperado = eval_f(eq_base, row.c)
            assert abs(row.fc - fc_esperado) < 1e-12

    def test_x_new_igual_a_c(self, eq_base, params_intervalo_valido):
        """x_new debe coincidir con c en cada fila (bisección usa c como nueva aproximación)."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        for row in result.iterations:
            assert abs(row.x_new - row.c) < 1e-14

    def test_error_decreciente_en_promedio(self, eq_base, params_intervalo_valido):
        """El error en la última fila debe ser menor que en la segunda fila (k=1)."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        errors = [r.error_pct for r in result.iterations if r.error_pct is not None]
        if len(errors) >= 2:
            assert errors[-1] < errors[0]

    def test_ultima_fila_converged_true(self, eq_base, params_intervalo_valido):
        """La última fila de una ejecución convergente debe tener converged=True."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        if result.converged:
            assert result.iterations[-1].converged is True

    def test_root_coincide_con_c_final(self, eq_base, params_intervalo_valido):
        """El root reportado debe coincidir con el c de la última fila."""
        result = run(eq_base, params_intervalo_valido, a=0.0, b=1.0)
        assert abs(result.root - result.iterations[-1].c) < 1e-14
