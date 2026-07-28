# VISION_PLATAFORMA.md — El norte del proyecto

> Este documento describe HACIA DÓNDE va el proyecto (la visión y el diseño).
> Es complementario al CLAUDE.md, que describe el ESTADO TÉCNICO actual.
> - CLAUDE.md responde: "¿qué está hecho y cómo está el código hoy?"
> - VISION_PLATAFORMA.md responde: "¿qué estamos construyendo y en qué orden?"
> Última actualización: 2026-07-27 (FASE 2 cerrada: Aprender con teoría y telaraña).

---

## 1. La visión en una frase

No es una calculadora de métodos numéricos. Es una **plataforma de matemática
computacional** para que un estudiante **aprenda**, donde "Métodos Numéricos para
ecuaciones no lineales" es el PRIMER módulo de varios (el siguiente planeado:
Sistemas de Ecuaciones).

Metáfora rectora: **un edificio de varios pisos.** Hoy construimos un piso bien
hecho (Métodos Numéricos), pero los cimientos se diseñan para soportar muchos.

---

## 2. Arquitectura de dos niveles

```
PLATAFORMA (el edificio)
│
├── Vestíbulo / inicio  → el estudiante elige el MÓDULO
│
├── MÓDULO: Métodos Numéricos (ecuaciones no lineales)   ← el de hoy
│     ├── Pestaña APRENDER
│     ├── Pestaña PRACTICAR
│     └── Pestaña CALCULAR
│
├── MÓDULO: Sistemas de Ecuaciones   ← futuro (tras avanzar en cálculo vectorial)
│     └── (sus propias pestañas)
│
└── MÓDULO: (futuros)
```

**Decisiones de diseño tomadas:**
- Vestíbulo: **Filosofía A** — el estudiante entra y elige su intención/módulo
  (no cae directo en la calculadora).
- Dentro de cada módulo: **pestañas** (Aprender / Practicar / Calcular) para que
  el estudiante salte fluido entre comprender, hacer y verificar.
- Nombre de la plataforma: **NumériCa** (decidido 2026-07-21).
  **NumériCa — plataforma de matemática computacional académica.**
  ("Métodos Numéricos" pasa a ser el nombre del PRIMER MÓDULO, no del conjunto.)

---

## 3. Las tres pestañas del módulo (progresión pedagógica)

La secuencia NO es arbitraria: es **comprende → construye → verifica**, tres
niveles de dominio creciente.

### APRENDER — "entiende cómo funciona"
- Teoría de cada método (qué es, fórmula, cuándo aplica, orden de convergencia).
- Las fórmulas se renderizan con KaTeX (YA implementado en la calculadora).
- **Debajo: demostración gráfica INTERACTIVA** del método (la pieza estrella).
  - El estudiante elige sus parámetros (x₀, intervalo) sobre el gráfico y ve,
    paso a paso, CÓMO converge el método con su propia función.
  - **Cada familia de método necesita su propia visualización:**
    - Punto fijo / Aitken / Steffensen → diagrama de telaraña (cobweb): g(x),
      la recta y=x, y la espiral de iteraciones que converge a la raíz.
    - Bisección / Regula Falsi → el intervalo [a,b] que se parte y encoge.
    - Newton / Newton 2º / Modificado → rectas tangentes que bajan al eje.
    - Secante → rectas que cruzan dos puntos.
  - **Prueba de concepto inicial: la TELARAÑA de punto fijo** (ya diseñada en
    detalle por el autor; es el cobweb plot canónico, herramienta estándar para
    enseñar convergencia de punto fijo). Si esta funciona y se ve bien, se vuelve
    la plantilla para adaptar a los demás tipos.
    **✅ CONSTRUIDA en FASE 2.** Lo que deja como plantilla reutilizable: escala
    isométrica (obligatoria para que la diagonal se vea a 45°), iteración en
    cliente (el backend no devuelve trayectorias que divergen), la divergencia
    dibujada y explicada, paso a paso con animación, y la paleta que sigue al tema.

### PRACTICAR — "constrúyelo tú mismo"
- Objetivo: que el estudiante aprenda a **construir las fórmulas paso a paso**,
  como se hace en la hoja Excel de referencia.
- **DECISIÓN CLAVE — Excel SIMULADO, no Excel real embebido.**
  - NO se embebe un Excel funcional de Microsoft (técnicamente costosísimo:
    requeriría servicios de pago/autenticación de Microsoft, o reconstruir Excel
    entero dentro de la web).
  - SÍ se construye una **tabla interactiva tipo hoja de cálculo, propia**, donde
    el estudiante escribe las fórmulas y el sistema le dice si están bien, le
    marca errores y le explica por qué. Es una *simulación educativa* que el
    proyecto controla.
  - Esto es MEJOR que Excel real para enseñar: Excel real no guía ni corrige; la
    simulación sí. Es el "constructor de Excel paso a paso" = el diferenciador
    único del proyecto.
- Acompañamiento en pantalla (para que el alumno se enfoque en aprender la
  construcción, no en calcular a mano):
  - Un gráfico x-y (se reutiliza la visualización de Aprender) para ver la
    función y elegir puntos iniciales / intervalos.
  - Al lado: la derivada, la segunda derivada y el g(x) predeterminados (el
    backend YA los genera; solo mostrarlos).
- **Ejercicios propuestos que rotan cada semana automáticamente** (banco de
  ejercicios que rota por fecha). Pieza de fase posterior.

### CALCULAR — "verifica tu trabajo"
- La calculadora actual, tal cual ya existe (resolver, resolver todos, tabla de
  iteraciones, teoría KaTeX, descarga de Excel con fórmulas nativas).
- El estudiante entra, pone su ecuación, comprueba su resultado. Fin del ciclo.

---

## 4. Plan de construcción por fases (de menor a mayor riesgo)

Regla de oro: **un piso bien hecho antes de los diez.** Cada fase es verificable
y construye sobre la anterior.

**FASE 0 — Cerrar los bugs pendientes.** ✅ CERRADA (2026-06-18)
- G1 (gráfico no auto-encuadra), G2 (marcador fantasma x≈0, backend),
  G7 (Excel falso "sin raíces reales", backend), G4 (banner sticky),
  G5 (cold-start de Render contamina la experiencia) → **todos resueltos y
  verificados en vivo.** (Detalle técnico y commits en CLAUDE.md §7.)
- G2 y G7 fueron de la misma familia (detección de raíces en backend) → se
  atacaron juntos (compartían causa: realidad de raíces vía `is_real`).
- Cimientos sólidos antes de construir encima. → **Listo para FASE 1.**

**FASE 1 — Esqueleto de navegación.** ✅ CERRADA (2026-07-22)
- Estructura de la plataforma (vestíbulo) + pestañas del módulo, con react-router **v7**.
- Las pestañas existen pero solo CALCULAR tiene contenido (ya existía). Aprender y
  Practicar quedan como esqueleto navegable, cada una anunciando qué vivirá ahí y
  en qué fase (una página en blanco parece un bug).
- Es "el edificio con sus pisos" aunque los pisos estén casi vacíos.
- Commits `6e9eeb4` (dependencia) + `267b349` (esqueleto). Detalle técnico, rutas y
  verificación en CLAUDE.md §5. Backend intacto (0 cambios, 152 tests sin tocar).
- **Deuda asumida a propósito:** el estado no se comparte entre pestañas; cambiar de
  pestaña reinicia la calculadora. Irrelevante hoy (Aprender y Practicar están vacías),
  pero hay que resolverlo en FASE 3, donde Practicar reutiliza gráfico y derivadas.
  → **Listo para FASE 2.**

**FASE 2 — Llenar APRENDER.** ✅ CERRADA (2026-07-27)
- **Teoría de los 14 métodos**, con las fórmulas en KaTeX: qué hace cada uno, con
  qué recurrencia itera, qué condición necesita y a qué velocidad converge.
  Agrupados por las cinco familias, con la ficha completa a la vista.
- **La TELARAÑA de punto fijo, interactiva y viva**: el estudiante elige la
  ecuación, prueba distintos reordenamientos g(x) —o escribe el suyo—, mueve x₀ y
  ve la escalera avanzar paso a paso. La prueba de concepto que pedía §3 **funciona
  y ya es la plantilla** para las demás familias en FASE 4.
- **La lección se ve, no se enuncia:** la misma ecuación con tres g(x) distintas,
  una que atrae y dos que repelen, con su |g′| medido en pantalla. La divergencia
  se dibuja y se explica en vez de esconderse — que es justo lo que la calculadora
  no puede hacer, porque se niega a iterar cuando no hay garantía de convergencia.
- **Tres fichas dicen la verdad incómoda:** punto fijo, Newton 2º orden y Ostrowsky
  llevan un apartado "En este proyecto" que reconoce ante el alumno dónde la
  implementación se aparta de lo canónico. Una herramienta académica que esconde
  eso enseña mal.
- **Backend: cero cambios.** Una decisión planeada de tocarlo se revirtió al medir
  que su premisa era falsa; los 152 tests no se ejecutaron porque nada los roza.
- Detalle técnico, commits, hallazgos y bugs (G11, G12) en CLAUDE.md §5.
- **Salvedad honesta:** toda la fase se verificó por medición del DOM y de los
  píxeles del lienzo, **sin una sola captura de pantalla**. Está comprobado *qué* se
  dibuja y *dónde*; el juicio estético sigue siendo del autor. → **Listo para FASE 3.**

**FASE 3 — Llenar PRACTICAR.**
- El constructor de fórmulas simulado + gráfico + derivadas/g(x) mostrados.
- **Deja de ser aplazable la deuda de FASE 1:** hoy cada pestaña tiene su propio
  estado y cambiar de pestaña reinicia la calculadora. Era irrelevante mientras
  Aprender y Practicar estaban vacías; con Practicar reutilizando gráfico y
  derivadas (§3), el estudiante perdería su trabajo al navegar. Hay que subir la
  ecuación a estado del módulo antes de construir encima.
- **Lo que FASE 2 deja hecho y Practicar hereda:** el evaluador de expresiones en
  cliente, el motor de iteración, el lienzo con paleta de tema y el catálogo de
  teoría. Practicar no arranca de cero: arranca de esas piezas.
- **Decisión pendiente antes de empezar:** de dónde salen los ejercicios. El banco
  rotativo por fecha (§3) es pieza de fase posterior, así que la primera versión
  necesita un conjunto fijo y curado, como se hizo con los g(x) de la telaraña.

**FASE 4 — Expansión.**
- Otras visualizaciones (bisección, Newton...), ejercicios semanales rotativos,
  más métodos numéricos, y el SEGUNDO MÓDULO (Sistemas de Ecuaciones) cuando el
  autor haya avanzado en cálculo vectorial.

---

## 5. Mejora de diseño visual (transversal)

El diseño actual se ve "simple y estructuralmente sencillo" (palabras del autor).
La plataforma necesita una identidad visual propia: un lenguaje que comunique
"herramienta académica seria". Esto se aborda DESPUÉS de tener clara la estructura
(primero el plano, luego la estética). No decidir colores antes de saber cuántas
habitaciones hay.

---

## 6. Qué NO hacer (decisiones explícitas, para no repetir debates)

- NO embeber Excel real de Microsoft. Se hace constructor simulado propio.
- NO diseñar el módulo de Sistemas de Ecuaciones todavía (su matemática llega con
  el cálculo vectorial del autor). Solo dejar la plataforma lista para recibirlo.
- NO intentar las 14 visualizaciones a la vez. Una (telaraña de punto fijo)
  perfecta primero, como plantilla.
- NO construir lo vistoso sobre bugs sin cerrar. Fase 0 primero.
- NO instalar MathQuill/MathLive (ya decidido: se usa el normalizador propio).
