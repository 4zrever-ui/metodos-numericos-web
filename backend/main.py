from backend.core.equation_parser import parse_equation
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