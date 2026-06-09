import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from excel.excel_generator import _default_params
from core.auto_params import generate_params
from core.equation_parser import parse_equation

print("=== TEST _default_params ===")
p = _default_params('biseccion', 'x**3 - 2*x - 5')
print("biseccion:", p)

p2 = _default_params('punto_fijo', 'x**3 - 2*x - 5')
print("punto_fijo:", p2)

print("\n=== TEST generate_params directo ===")
eq = parse_equation('x**3 - 2*x - 5')
ap = generate_params(eq)
print("a:", ap.a, "  b:", ap.b)
print("x0:", ap.x0, "  x0_alt:", ap.x0_alt)
print("gx_sympy:", ap.gx_sympy)
print("gx_excel:", ap.gx_excel)