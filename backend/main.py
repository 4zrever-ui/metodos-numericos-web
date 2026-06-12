from backend.core.equation_parser import parse_equation
from backend.core.auto_params import generate_params
from backend.methods.newton_raphson import run as run_newton
from backend.methods.biseccion import run as run_biseccion
from backend.methods.regula_falsi import run as run_regula_falsi
from backend.methods.secante import run as run_secante
from backend.methods.punto_fijo import run as run_punto_fijo
from backend.methods.steffensen import run as run_steffensen
from backend.methods.aitken import run as run_aitken
from backend.methods.von_mises import run as run_von_mises
from backend.methods.newton_family import (
    run_newton_modificado,
    run_newton_segundo_orden,
    run_chebyshev,
    run_halley,
    run_super_halley,
    run_ostrowsky,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.excel.excel_generator import generate_single, generate_all, _has_real_roots
from backend.excel.excel_templates import _panel_message
import io

app = FastAPI(title="Métodos Numéricos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _x0(data):  return data.get("x0")    # None → auto
def _x1(data):  return data.get("x1")    # None → auto
def _a(data):   return data.get("a")     # None → auto
def _b(data):   return data.get("b")     # None → auto
def _tol(data): return data.get("tol", 0.00001)

def _eq(data, key="equation", default=""):
    """Extrae la ecuación y normaliza ^ → ** para que x^3 funcione igual que x**3."""
    raw = data.get(key, default) or default
    return raw.replace("^", "**")


@app.get("/")
def root():
    return {
        "mensaje": "API Métodos Numéricos funcionando"
    }

@app.post("/analyze")
def analyze(data: dict):

    equation = _eq(data)

    parsed = parse_equation(equation)

    return {
        "status": "ok",
        "equation": equation,
        "f_latex": parsed.f_latex,
        "fp_latex": parsed.fp_latex,
        "f_excel": parsed.f_excel,
        "fp_excel": parsed.fp_excel
    }

@app.post("/method/newton")
def method_newton(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/biseccion")
def method_biseccion(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_biseccion(eq, params, a=_a(data), b=_b(data), tol=_tol(data))

    return result

@app.post("/method/regula_falsi")
def method_regula_falsi(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_regula_falsi(eq, params, a=_a(data), b=_b(data), tol=_tol(data))

    return result

@app.post("/method/secante")
def method_secante(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_secante(eq, params, x0=_x0(data), x1=_x1(data), tol=_tol(data))

    return result

@app.post("/method/punto_fijo")
def method_punto_fijo(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_punto_fijo(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/steffensen")
def method_steffensen(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_steffensen(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/aitken")
def method_aitken(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_aitken(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/von_mises")
def method_von_mises(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_von_mises(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/newton_modificado")
def method_newton_modificado(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton_modificado(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/newton_segundo_orden")
def method_newton_segundo_orden(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton_segundo_orden(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/chebyshev")
def method_chebyshev(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_chebyshev(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/halley")
def method_halley(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_halley(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/super_halley")
def method_super_halley(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_super_halley(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/ostrowsky")
def method_ostrowsky(data: dict):

    equation = _eq(data)

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_ostrowsky(eq, params, x0=_x0(data), tol=_tol(data))

    return result


@app.post("/diagnose")
def diagnose(data: dict):
    """
    Explicación clara cuando un método no aplica o no converge. Reutiliza la
    misma lógica que el panel del Excel (causa real + mensaje en lenguaje
    simple), para no duplicarla en el frontend.
    """
    equation   = _eq(data)
    method_key = data.get("method_key", "")
    applicable = data.get("applicable", True)

    KEY_MAP = {"newton": "newton_raphson", "newton_segundo_orden": "newton_2do_orden"}
    method_key = KEY_MAP.get(method_key, method_key)

    has_roots = _has_real_roots(equation)
    title, body, suggestion = _panel_message(method_key, applicable, has_roots)
    return {
        "has_real_roots": has_roots,
        "title": title,
        "body": body,
        "suggestion": suggestion,
    }


# ---------------------------------------------------------------------------
# Bloque 2 — Endpoints nuevos: comparativa + exportación Excel
# ---------------------------------------------------------------------------

ALL_METHOD_RUNNERS = [
    ("newton",               lambda eq, p, d: run_newton(eq, p, x0=_x0(d), tol=_tol(d))),
    ("biseccion",            lambda eq, p, d: run_biseccion(eq, p, a=_a(d), b=_b(d), tol=_tol(d))),
    ("regula_falsi",         lambda eq, p, d: run_regula_falsi(eq, p, a=_a(d), b=_b(d), tol=_tol(d))),
    ("secante",              lambda eq, p, d: run_secante(eq, p, x0=_x0(d), x1=_x1(d), tol=_tol(d))),
    ("punto_fijo",           lambda eq, p, d: run_punto_fijo(eq, p, x0=_x0(d), tol=_tol(d))),
    ("steffensen",           lambda eq, p, d: run_steffensen(eq, p, x0=_x0(d), tol=_tol(d))),
    ("aitken",               lambda eq, p, d: run_aitken(eq, p, x0=_x0(d), tol=_tol(d))),
    ("von_mises",            lambda eq, p, d: run_von_mises(eq, p, x0=_x0(d), tol=_tol(d))),
    ("newton_modificado",    lambda eq, p, d: run_newton_modificado(eq, p, x0=_x0(d), tol=_tol(d))),
    ("newton_segundo_orden", lambda eq, p, d: run_newton_segundo_orden(eq, p, x0=_x0(d), tol=_tol(d))),
    ("chebyshev",            lambda eq, p, d: run_chebyshev(eq, p, x0=_x0(d), tol=_tol(d))),
    ("halley",               lambda eq, p, d: run_halley(eq, p, x0=_x0(d), tol=_tol(d))),
    ("super_halley",         lambda eq, p, d: run_super_halley(eq, p, x0=_x0(d), tol=_tol(d))),
    ("ostrowsky",            lambda eq, p, d: run_ostrowsky(eq, p, x0=_x0(d), tol=_tol(d))),
]


@app.post("/method/all")
def method_all(data: dict):
    """Ejecuta los 14 métodos y devuelve tabla comparativa JSON."""
    equation = _eq(data)
    eq = parse_equation(equation)
    params = generate_params(eq)

    results = []
    for method_key, runner in ALL_METHOD_RUNNERS:
        try:
            result = runner(eq, params, data)
            results.append({
                "method":          method_key,
                "applicable":      getattr(result, "applicable", True),
                "converged":       getattr(result, "converged", False),
                "root":            getattr(result, "root", None),
                "iteration_count": getattr(result, "iteration_count", None),
                "final_error_pct": getattr(result, "final_error_pct", None),
                "reason":          getattr(result, "reason", ""),
            })
        except Exception as e:
            results.append({
                "method":          method_key,
                "applicable":      False,
                "converged":       False,
                "root":            None,
                "iteration_count": None,
                "final_error_pct": None,
                "reason":          str(e),
            })

    return {"equation": equation, "results": results}


@app.post("/excel/single")
def excel_single(data: dict):
    """Genera y descarga un Excel de un método individual."""
    equation   = _eq(data)
    method_key = data.get("method_key", "newton_raphson")

    KEY_MAP = {
        "newton":               "newton_raphson",
        "newton_segundo_orden": "newton_2do_orden",
    }
    method_key = KEY_MAP.get(method_key, method_key)

    xlsx_bytes = generate_single(method_key, equation, eq_label=equation)
    filename   = f"metodos_numericos_{method_key}.xlsx"

    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/excel/all")
def excel_all(data: dict):
    """Genera y descarga un Excel con los 14 métodos en hojas separadas."""
    equation = _eq(data)

    xlsx_bytes = generate_all(equation, eq_label=equation)

    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=metodos_numericos_todos.xlsx"},
    )