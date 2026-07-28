"""
Especificación de las fórmulas de cada método, COMO DATO.

Para qué existe
---------------
La pestaña Practicar enseña a construir la hoja de cálculo celda a celda: el
alumno escribe la fórmula y el sistema le dice si hace lo mismo que la correcta.
Para eso hace falta la fórmula correcta *como cadena*, y hasta ahora sólo existía
como efecto secundario de escribir un .xlsx (`/excel/*` devuelve binario).

Por qué es un módulo aparte y no un refactor de `excel_templates.py`
--------------------------------------------------------------------
Porque ese archivo —1091 líneas, donde vive cada fórmula de cada método— **no
tiene ningún test** (hallazgo H3 en CLAUDE.md §7: el único import de Excel en
toda la suite es `_has_real_roots`, de `excel_generator`). Tocarlo sería trabajar
sin red: un fallo no lo atraparía la suite y sólo aparecería al abrir un Excel
descargado.

La contrapartida de duplicar es que las dos copias pueden divergir. Eso lo cierra
`test/test_formula_specs.py`, que **construye la hoja de verdad con la plantilla
real, en memoria, y comprueba celda a celda que coincide con lo que hay aquí**.
Si alguien cambia la plantilla, ese test se rompe.

Alcance: Newton-Raphson y Bisección (decisión D5 — uno de derivada y uno de
intervalo antes de extender a los catorce).

Lo que NO se expone: el envoltorio `_freeze`
--------------------------------------------
Las plantillas envuelven cada fórmula en un `IF(...)` que deja la celda en blanco
tras converger. Su propio docstring lo llama "puramente presentacional", y
decisión D4 es no enseñárselo al alumno: convertiría un ejercicio de método
numérico en uno de lógica de Excel. Aquí se guarda la fórmula limpia — que es
exactamente la que la plantilla escribe en la fila k=0, donde `_freeze` es la
identidad.
"""

from __future__ import annotations

from ..core.sympy_to_excel import to_excel_formula

# Tolerancia de convergencia que usan las plantillas, en las columnas de "SI/NO".
_TOL_EXCEL = "0.00001"


def _col(letra: str, cabecera: str, formula, explicacion: str, literal_en_k0: str | None = None,
         vacia_en_k0: bool = False) -> dict:
    """Una columna de la hoja. `formula` es (fila) -> cadena sin el '=' inicial."""
    return {
        "columna": letra,
        "cabecera": cabecera,
        "formula": formula,
        "explicacion": explicacion,
        "literal_en_k0": literal_en_k0,
        "vacia_en_k0": vacia_en_k0,
    }


def newton_raphson(fx: str, fpx: str) -> dict:
    """
    Newton-Raphson. Estructura tomada de `NewtonRaphsonTemplate`.

    En k=0 la columna B es el x₀ que teclea el alumno; a partir de k=1 arrastra
    el xₖ₊₁ de la fila anterior.
    """
    return {
        "metodo": "newton",
        "label": "Newton-Raphson",
        "primera_fila": 2,          # la fila 1 es la cabecera
        "columnas": [
            _col("A", "k", lambda r: str(r - 2), "El índice de la iteración. No es una fórmula.",
                 literal_en_k0="0"),
            _col("B", "xₖ", lambda r: f"E{r-1}",
                 "El xₖ₊₁ que calculó la fila anterior pasa a ser el xₖ de ésta.",
                 literal_en_k0="x₀"),
            _col("C", "f(xₖ)", lambda r: to_excel_formula(fx, f"B{r}"),
                 "La función evaluada en xₖ. Sustituye la x por la celda B de esta fila."),
            _col("D", "f'(xₖ)", lambda r: to_excel_formula(fpx, f"B{r}"),
                 "La derivada evaluada en el mismo punto."),
            _col("E", "xₖ₊₁", lambda r: f"B{r}-(C{r}/D{r})",
                 "El paso de Newton: al punto actual se le resta f(xₖ)/f'(xₖ)."),
            _col("F", "Error %", lambda r: f"ABS((E{r}-B{r})/E{r})*100",
                 "Error relativo porcentual entre la aproximación nueva y la anterior."),
            _col("G", "Convergencia", lambda r: f'IF(F{r}<{_TOL_EXCEL},"SI","NO")',
                 "Compara el error con la tolerancia y responde SI o NO."),
        ],
    }


def biseccion(fx: str, _fpx: str = "") -> dict:
    """
    Bisección. Estructura tomada de `BiseccionTemplate`.

    OJO — esto NO es simétrico con Newton, y el sondeo D2 lo midió: en la fila
    k=0 las columnas B (a) y D (b) son los LITERALES del intervalo inicial, y las
    columnas I y J están VACÍAS. Las fórmulas de actualización del intervalo sólo
    aparecen desde k=1. Por eso el test las verifica en la fila 3, no en la 2.
    """
    return {
        "metodo": "biseccion",
        "label": "Bisección",
        "primera_fila": 2,
        "columnas": [
            _col("A", "k", lambda r: str(r - 2), "El índice de la iteración. No es una fórmula.",
                 literal_en_k0="0"),
            _col("B", "a", lambda r: f"IF(E{r-1}*F{r-1}<0,B{r-1},C{r-1})",
                 "Si f(a)·f(c) cambió de signo, la raíz está en la mitad izquierda y a se "
                 "queda; si no, a pasa a ser c.",
                 literal_en_k0="a₀"),
            _col("C", "c=(a+b)/2", lambda r: f"(B{r}+D{r})/2",
                 "El punto medio del intervalo de esta fila."),
            _col("D", "b", lambda r: f"IF(E{r-1}*F{r-1}<0,C{r-1},D{r-1})",
                 "El extremo derecho, con el criterio espejo del de a.",
                 literal_en_k0="b₀"),
            _col("E", "f(a)", lambda r: to_excel_formula(fx, f"B{r}"), "La función en el extremo izquierdo."),
            _col("F", "f(c)", lambda r: to_excel_formula(fx, f"C{r}"), "La función en el punto medio."),
            _col("G", "f(b)", lambda r: to_excel_formula(fx, f"D{r}"), "La función en el extremo derecho."),
            _col("H", "f(a)·f(c)", lambda r: f"E{r}*F{r}",
                 "El producto que decide con qué mitad se sigue: negativo = la raíz está entre a y c."),
            _col("I", "Error %", lambda r: f"ABS((C{r}-C{r-1})/C{r})*100",
                 "Error relativo entre el punto medio de esta fila y el de la anterior.",
                 vacia_en_k0=True),
            _col("J", "Convergencia", lambda r: f'IF(I{r}<{_TOL_EXCEL},"SI","NO")',
                 "Compara el error con la tolerancia y responde SI o NO.",
                 vacia_en_k0=True),
        ],
    }


ESPECIFICACIONES = {
    "newton": newton_raphson,
    "biseccion": biseccion,
}


def spec_para(metodo: str, fx: str, fpx: str = "") -> dict | None:
    """Devuelve la especificación de un método, o None si no está cubierto."""
    constructor = ESPECIFICACIONES.get(metodo)
    if constructor is None:
        return None
    return constructor(fx, fpx)


def spec_serializable(metodo: str, fx: str, fpx: str = "", fila: int = 3) -> dict | None:
    """
    La especificación con las fórmulas ya resueltas para una fila concreta,
    lista para enviar por JSON (las lambdas no se serializan).

    `fila` por defecto es la 3 —es decir k=1— a propósito: es la primera fila
    donde TODAS las columnas son fórmulas. En la fila 2 (k=0) varias son
    literales o están vacías, y en Bisección eso incluye justo las dos más
    interesantes, las del intervalo.
    """
    spec = spec_para(metodo, fx, fpx)
    if spec is None:
        return None

    return {
        "metodo": spec["metodo"],
        "label": spec["label"],
        "fila": fila,
        "k": fila - 2,
        "columnas": [
            {
                "columna": c["columna"],
                "cabecera": c["cabecera"],
                "formula": "=" + c["formula"](fila),
                "explicacion": c["explicacion"],
                "literal_en_k0": c["literal_en_k0"],
                "vacia_en_k0": c["vacia_en_k0"],
            }
            for c in spec["columnas"]
        ],
    }


def spec_hoja(metodo: str, fx: str, fpx: str = "", n_filas: int = 6,
              valores_iniciales: dict | None = None) -> dict | None:
    """
    La hoja entera, fila a fila, lista para que el frontend la dibuje y la
    resuelva.

    Cada celda dice de qué tipo es, que es lo que el constructor necesita saber
    para decidir si se teclea o viene dada:
        "indice"   el k, un entero
        "inicial"  un literal que pone el alumno (x₀, a₀, b₀)
        "formula"  la que hay que escribir
        "vacia"    en Bisección, el error y la convergencia de la fila k=0

    La distinción NO es cosmética: en Bisección las columnas del intervalo son
    literales en k=0 y fórmulas desde k=1, y tratarlas por simetría con Newton
    daría una hoja incorrecta (sondeo D2).
    """
    spec = spec_para(metodo, fx, fpx)
    if spec is None:
        return None

    iniciales = valores_iniciales or {}
    # Qué literal le toca a cada columna en la fila k=0.
    claves = {"x₀": "x0", "a₀": "a0", "b₀": "b0"}

    filas = []
    for i in range(n_filas):
        fila_excel = spec["primera_fila"] + i
        k = i
        celdas = []
        for c in spec["columnas"]:
            if c["columna"] == "A":
                tipo, contenido = "indice", str(k)
            elif k == 0 and c["vacia_en_k0"]:
                tipo, contenido = "vacia", ""
            elif k == 0 and c["literal_en_k0"] is not None:
                clave = claves.get(c["literal_en_k0"])
                valor = iniciales.get(clave) if clave else None
                tipo, contenido = "inicial", ("" if valor is None else str(valor))
            else:
                tipo, contenido = "formula", "=" + c["formula"](fila_excel)

            celdas.append({
                "columna": c["columna"],
                "ref": f"{c['columna']}{fila_excel}",
                "tipo": tipo,
                "contenido": contenido,
                "explicacion": c["explicacion"],
            })
        filas.append({"k": k, "fila": fila_excel, "celdas": celdas})

    return {
        "metodo": spec["metodo"],
        "label": spec["label"],
        "cabeceras": [
            {"columna": c["columna"], "cabecera": c["cabecera"]} for c in spec["columnas"]
        ],
        "filas": filas,
    }
