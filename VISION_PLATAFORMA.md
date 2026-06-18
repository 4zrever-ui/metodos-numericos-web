# VISION_PLATAFORMA.md — El norte del proyecto

> Este documento describe HACIA DÓNDE va el proyecto (la visión y el diseño).
> Es complementario al CLAUDE.md, que describe el ESTADO TÉCNICO actual.
> - CLAUDE.md responde: "¿qué está hecho y cómo está el código hoy?"
> - VISION_PLATAFORMA.md responde: "¿qué estamos construyendo y en qué orden?"
> Última actualización: 2026-06-17.

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
- Nombre de la plataforma: PENDIENTE de decidir ("Métodos Numéricos" ya no
  alcanza como nombre del conjunto).

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

**FASE 1 — Esqueleto de navegación.**
- Estructura de la plataforma (vestíbulo) + pestañas del módulo, con react-router.
- Las pestañas existen pero solo CALCULAR tiene contenido (ya existe). Aprender y
  Practicar quedan como esqueleto navegable.
- Es "el edificio con sus pisos" aunque los pisos estén casi vacíos.

**FASE 2 — Llenar APRENDER.**
- Teoría por método (con KaTeX) + la TELARAÑA interactiva de punto fijo como
  prueba de concepto. Si funciona y se ve bien, plantilla para las demás.

**FASE 3 — Llenar PRACTICAR.**
- El constructor de fórmulas simulado + gráfico + derivadas/g(x) mostrados.

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
