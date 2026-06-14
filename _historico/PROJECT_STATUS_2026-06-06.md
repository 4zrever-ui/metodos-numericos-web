ESTADO ACTUAL

Archivos de referencia válidos:

- EXCEL_COMPATIBILITY_[SPEC.md](http://SPEC.md)

- AUTO_PARAMS_CURRENT_[STATE.md](http://STATE.md)

- MULTI_EQUATION_CURRENT_[AUDIT.md](http://AUDIT.md)

Backend matemático:

- 14/14 métodos compatibles con Excel.

- SPEC congelado.

- No modificar métodos numéricos.

Problemas pendientes:

1. auto_[params.py](http://params.py)

   - g(x) hardcodeada para x³−2x−5.

   - estrategias S1-S4 comentadas.

   - Punto Fijo, Aitken y Steffensen solo funcionan bien para x³−2x−5.

2. selección de x0

   - para raíces negativas puede elegir x0=0.

   - provoca f'(0)=0 y deja 8 métodos como NOT_APPLICABLE.

3. secante

   - hereda el problema anterior y converge a la raíz negativa.

Objetivo siguiente:

Reparar auto_[params.py](http://params.py) sin tocar los 14 métodos congelados.

Antes de cualquier cambio:

ejecutar audit_[backend.py](http://backend.py)

Después de cualquier cambio:

ejecutar audit_[backend.py](http://backend.py) nuevamente y mantener 14/14 PASS.