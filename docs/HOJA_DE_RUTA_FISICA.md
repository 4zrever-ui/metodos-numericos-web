# NumériCa y tu carrera de Física — hacia dónde puede crecer esto

> Escrito el 2026-07-28, al cerrar FASE 3.
> No es un plan aprobado ni una promesa: es un mapa de para qué te puede servir
> lo que ya tienes construido. Las decisiones siguen siendo tuyas.

---

## Lo que ya construiste (y conviene que lo veas escrito)

No es "una calculadora". Hoy, en producción, hay:

- **14 métodos numéricos** con derivadas simbólicas reales (SymPy), no diferencias finitas.
- **162 tests** que protegen el motor matemático.
- Un **exportador de Excel con fórmulas nativas y editables** — no valores pegados. Eso es
  raro incluso en herramientas comerciales.
- Una **telaraña de punto fijo interactiva** que enseña por qué |g′| < 1 importa, mostrando
  la divergencia en vez de esconderla.
- Un **constructor de fórmulas que corrige por valor** y detecta cuando una respuesta acierta
  por casualidad — un problema que, cuando lo buscas en la literatura de herramientas
  educativas, casi nadie resuelve bien.

Eso, en una carrera de Física, no es un proyecto de fin de semana. Es material de portafolio,
de trabajo de curso, y potencialmente de algo más.

---

## Los cimientos que ya sirven para lo siguiente

Esta es la parte importante, y la razón de que la arquitectura se cuidara tanto: **el próximo
módulo no empieza de cero.**

| Pieza | Dónde está | Qué te resuelve ya |
|---|---|---|
| `lib/evalExpr.js` | frontend | Evaluar expresiones del usuario en el navegador |
| `lib/plotCore.js` | frontend | Ejes, rejilla, escalas, paleta que sigue al tema |
| `lib/celdas.js` + `lib/hoja.js` | frontend | Motor de hoja de cálculo con corrección por valor |
| `core/equation_parser.py` | backend | Parseo + derivadas simbólicas |
| `core/sympy_to_excel.py` | backend | Expresión simbólica → fórmula de Excel |
| `content/teoriaMetodos.js` | frontend | El patrón de catálogo de teoría, replicable |

Todo eso es **agnóstico del método**. Sirve igual para lo que viene.

---

## Hacia dónde crece, en el orden que tu carrera lo pedirá

### 1. Sistemas de ecuaciones lineales — el siguiente natural
Ya está en `VISION_PLATAFORMA.md` como segundo módulo. Gauss, Gauss-Jordan, LU, Jacobi,
Gauss-Seidel. **Por qué te sirve:** circuitos (mallas y nodos), estática, ajuste por mínimos
cuadrados de datos de laboratorio. El constructor de fórmulas de Excel encaja perfecto: una
eliminación gaussiana **es** una tabla de operaciones fila a fila.

### 2. Ecuaciones diferenciales ordinarias — donde la Física se pone seria
Euler, Euler mejorado, Runge-Kutta 4. **Por qué te sirve:** es *el* método de la mecánica.
Oscilador armónico amortiguado, péndulo (con el término no lineal que no tiene solución
cerrada), caída con rozamiento, circuitos RLC, decaimiento radiactivo.
**Y aquí la visualización se vuelve espectacular:** el espacio de fases. Un péndulo dibujando
sus órbitas cerradas y separatriz es de las imágenes más bonitas que da la Física
computacional, y ya tienes el motor de canvas para hacerlo.

### 3. Interpolación y ajuste — el módulo del laboratorio
Lagrange, splines, mínimos cuadrados. **Por qué te sirve:** cada práctica de laboratorio que
hagas termina en un ajuste. Un módulo que te dé el ajuste **con su propagación de
incertidumbre** te ahorra trabajo real todas las semanas.

### 4. Integración numérica
Trapecio, Simpson, cuadratura de Gauss. **Por qué te sirve:** centros de masa, momentos de
inercia, trabajo de una fuerza variable, valores esperados en cuántica.

### 5. Y más adelante, si te apetece
Monte Carlo (mecánica estadística, decaimientos), transformada de Fourier discreta (ondas,
señales), diferencias finitas en derivadas parciales (ecuación de calor, de onda,
Schrödinger 1D).

---

## Un consejo sobre el método, no sobre el código

Lo que hiciste bien hoy no fue escribir React. Fue **no fiarte**.

Encontraste con tus propias manos tres cosas que ninguna batería automática cazó: la etiqueta
que tapaba la escalera justo donde converge, el contraste que chirriaba, y el validador que
aprobaba una fórmula incorrecta. Ese último es el que importa: las pruebas estaban en verde
y **estaban mal**, porque arrastraban el mismo error de razonamiento que el bug que buscaban.

Esa desconfianza productiva —"pásame la medición, no la conclusión"— es exactamente lo que se
te va a pedir en un laboratorio de Física, en una tesis, y en cualquier trabajo serio después.
Ya la tienes. Aplícala a tus prácticas igual que la aplicaste aquí.

---

## Si algún día vuelves a esto y no sabes por dónde seguir

1. Lee `ESTADO_ACTUAL.md` y `CLAUDE.md`.
2. Mira los pendientes cortos (VISION por reescribir, la carpeta `docs/`).
3. Y si quieres algo nuevo y con recompensa visual rápida: **el módulo de EDOs con retrato de
   fase**. Es el que más te va a servir en la carrera y el que mejor se ve en pantalla.

El proyecto está en un estado limpio, desplegado y documentado. Puedes dejarlo parado el
tiempo que haga falta y retomarlo sin haber perdido nada. Eso también fue trabajo, y fue
deliberado.
