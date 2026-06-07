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


@app.get("/")
def root():
    return {
        "mensaje": "API Métodos Numéricos funcionando"
    }

@app.post("/analyze")
def analyze(data: dict):

    equation = data.get("equation")

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

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/biseccion")
def method_biseccion(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_biseccion(eq, params, a=_a(data), b=_b(data), tol=_tol(data))

    return result

@app.post("/method/regula_falsi")
def method_regula_falsi(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_regula_falsi(eq, params, a=_a(data), b=_b(data), tol=_tol(data))

    return result

@app.post("/method/secante")
def method_secante(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_secante(eq, params, x0=_x0(data), x1=_x1(data), tol=_tol(data))

    return result

@app.post("/method/punto_fijo")
def method_punto_fijo(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_punto_fijo(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/steffensen")
def method_steffensen(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_steffensen(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/aitken")
def method_aitken(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_aitken(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/von_mises")
def method_von_mises(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_von_mises(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/newton_modificado")
def method_newton_modificado(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton_modificado(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/newton_segundo_orden")
def method_newton_segundo_orden(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_newton_segundo_orden(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/chebyshev")
def method_chebyshev(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_chebyshev(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/halley")
def method_halley(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_halley(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/super_halley")
def method_super_halley(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_super_halley(eq, params, x0=_x0(data), tol=_tol(data))

    return result

@app.post("/method/ostrowsky")
def method_ostrowsky(data: dict):

    equation = data.get("equation")

    eq = parse_equation(equation)

    params = generate_params(eq)

    result = run_ostrowsky(eq, params, x0=_x0(data), tol=_tol(data))

    return result
