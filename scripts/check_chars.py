#!/usr/bin/env python3
"""
Caza caracteres de alfabetos que este proyecto no usa, colados en el texto.

Por que existe
--------------
Se han colado tres veces glifos de otra escritura dentro de palabras por lo
demas en espanol: un ideograma CJK (U+63A7) y dos cirilicas en medio de la
palabra "genera" (U+0433, U+0435). A simple vista no se distinguen de las
latinas, y no los caza ningun linter: para ESLint y para pytest son texto
dentro de un comentario o de una cadena.

Que NO hace
-----------
No prohibe lo no-ASCII. El proyecto escribe en espanol y usa a diario tildes,
enes, y simbolos matematicos: pi, raices, superindices, flechas, guiones de
caja. Todo eso pasa. Solo se marcan ALFABETOS ajenos.

Uso
---
    python scripts/check_chars.py              # todo el repo
    python scripts/check_chars.py CLAUDE.md    # un archivo o carpeta suelta

Devuelve 1 si encuentra algo, 0 si esta limpio, para poder encadenarlo.
Es de invocacion MANUAL a proposito (decision del director, 2026-07-28): no es
un hook de pre-commit y no bloquea nada.

Excepcion
---------
Una linea que contenga el marcador `chars-ok` se salta. Sirve para los sitios
donde hay que citar el glifo a proposito -- sin el, este mismo archivo y la
regla 6.8 de CLAUDE.md se marcarian a si mismos.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

# (inicio, fin, nombre) de los bloques Unicode que este proyecto no usa.
RANGOS = [
    (0x0400, 0x04FF, "cirilico"),
    (0x0500, 0x052F, "cirilico suplementario"),
    (0x0590, 0x05FF, "hebreo"),
    (0x0600, 0x06FF, "arabe"),
    (0x0900, 0x097F, "devanagari"),
    (0x3040, 0x30FF, "kana"),
    (0x3400, 0x4DBF, "CJK extension A"),
    (0x4E00, 0x9FFF, "CJK"),
    (0xAC00, 0xD7AF, "hangul"),
    (0xF900, 0xFAFF, "CJK compatibilidad"),
]

EXTENSIONES = {".md", ".py", ".js", ".jsx", ".css", ".json", ".html", ".txt"}
OMITIR = {"node_modules", ".git", "dist", "build", "_historico",
          "validacion_c1", ".venv", "venv", "__pycache__", ".pytest_cache"}

MARCADOR_EXCEPCION = "chars-ok"


def bloque_de(cp: int) -> str | None:
    for inicio, fin, nombre in RANGOS:
        if inicio <= cp <= fin:
            return nombre
    return None


def archivos(raiz: Path):
    if raiz.is_file():
        yield raiz
        return
    for ruta in raiz.rglob("*"):
        if any(parte in OMITIR for parte in ruta.parts):
            continue
        if ruta.is_file() and ruta.suffix in EXTENSIONES:
            yield ruta


def revisar(raiz: Path) -> tuple[int, int]:
    hallazgos = 0
    revisados = 0

    for ruta in archivos(raiz):
        revisados += 1
        try:
            lineas = ruta.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        for n, linea in enumerate(lineas, 1):
            if MARCADOR_EXCEPCION in linea:
                continue
            for ch in linea:
                bloque = bloque_de(ord(ch))
                if bloque is None:
                    continue
                hallazgos += 1
                try:
                    nombre = unicodedata.name(ch)
                except ValueError:
                    nombre = "sin nombre"
                print(f"{ruta}:{n}  U+{ord(ch):04X} ({bloque}) — {nombre}")
                print(f"    {linea.strip()[:100]}")

    return revisados, hallazgos


def main() -> int:
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not raiz.exists():
        print(f"No existe: {raiz}")
        return 2

    revisados, hallazgos = revisar(raiz)
    print(f"\n{revisados} archivos revisados · {hallazgos} caracteres de alfabetos ajenos")
    if hallazgos:
        print("Revisa las lineas de arriba. Si el glifo esta ahi a proposito, "
              f"anade el marcador de excepcion a esa linea.")
    return 1 if hallazgos else 0


if __name__ == "__main__":
    raise SystemExit(main())
