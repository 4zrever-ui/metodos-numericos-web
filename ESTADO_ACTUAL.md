# ESTADO_ACTUAL.md — traspaso entre sesiones

> **Si acabas de abrir este proyecto: lee `CLAUDE.md` ENTERO primero, luego este archivo, y
> no propongas ningún cambio hasta haber hecho las dos cosas.**
>
> `CLAUDE.md` es la fuente de verdad del estado técnico. Este documento es sólo el mapa:
> dónde estamos, qué quedó sin resolver, y cómo se trabaja aquí.
>
> Última actualización: 2026-07-28, al agotarse la ventana de contexto de la sesión.

---

## 1. Dónde estamos exactamente

| Fase | Estado |
|---|---|
| **FASE 0** — Bugs (G1–G9) | ✅ Cerrada |
| **FASE 1** — Esqueleto de navegación | ✅ Cerrada |
| **FASE 2** — Llenar APRENDER | ✅ **Cerrada y desplegada** |
| **FASE 3** — Llenar PRACTICAR | ✅ **Construida, pusheada y verificada en producción** |
| **FASE 4** — Expansión | ⬜ **No iniciada** |

**FASE 2** dejó la pestaña Aprender con la teoría de los 14 métodos (KaTeX) y la telaraña
interactiva de punto fijo. En vivo.

**FASE 3** dejó Practicar funcionando: el constructor de fórmulas paso a paso, que es el
diferenciador del proyecto. Desplegado el 2026-07-28 (14 commits, `784f0c1..3a7fc25`) y
verificado **contra producción real** con cuatro pruebas — fórmula correcta, forma equivalente
aceptada, ramas de Bisección invertidas rechazadas (H4) y umbral falso rechazado (D3
multiescenario). El director las probó además a mano en local antes del push.

**Render auto-despliega desde `main`**: comprobado empíricamente en ese push (el endpoint pasó
de 404 a 200 en menos de dos minutos sin tocar el panel). Vercel también.

**FASE 4** no tiene ni plan escrito. Lo que hay son candidatos sueltos, abajo.

---

## 2. Lo que quedó pendiente, sin resolver

1. **`VISION_PLATAFORMA.md` necesita reescritura.** El borrador que existía quedó
   **desactualizado** tras los hallazgos H5 y H6 y tras el despliegue: seguía listando
   "desplegar el backend" como pendiente y no mencionaba ninguno de los dos hallazgos.
   **No está aplicado**, y el borrador vivía en el scratchpad de la sesión, así que
   probablemente ya no exista. Hay que rehacerlo desde el estado actual.
   Las decisiones D1–D7 sí estaban bien recogidas y siguen válidas (ver CLAUDE.md §5).

2. **Decisión sobre `docs/`.** Los 12 documentos históricos llevan ya una cabecera de aviso
   (`> [!WARNING] DOCUMENTO DESACTUALIZADO`), que era la medida mínima acordada. Queda por
   decidir qué hacer a medio plazo —moverlos a `_historico/`, revisarlos uno a uno, o dejarlos
   así— y **11 de los 12 siguen sin revisar**: sólo se comprobó `RESUMEN_PROYECTO.md`, donde se
   encontró que describe la interfaz como un `App.jsx` que no existe desde FASE 1. Ver **H6**.

3. **`/params` sigue silencioso ante fallos.** No es un bug de la familia de H5 (sí comprueba
   el campo de error), pero con el backend dormido el estudiante no ve parámetros sugeridos ni
   marcadores de raíz **sin ninguna explicación**. Es una decisión de UX pospuesta a propósito:
   la llamada se dispara casi en cada pulsación y hacerla ruidosa podría ser peor.
   Tres opciones ya anotadas en la deuda técnica de CLAUDE.md §7.

4. **Candidatos para FASE 4 en la telaraña**, registrados y **no construir antes**:
   zoom y desplazamiento interactivos, y refuerzo de color por recencia del trazo.
   El requisito no negociable del zoom ya está escrito: **debe escalar X e Y JUNTOS**
   (multiplicar el `scale` único de `isoView`), porque si la diagonal `y = x` deja de verse a
   45° se pierde toda la intuición del método. Ver CLAUDE.md §7.

**Y lo que no es técnico pero importa:** ninguna parte de FASE 2 ni FASE 3 se ha verificado
con **capturas de pantalla** — todo se midió sobre el DOM y los píxeles del lienzo. Está
comprobado *qué* se dibuja y *dónde*; el juicio estético sigue siendo del director.

---

## 3. Hallazgos con entrada propia (H1–H6)

Una línea cada uno. **El detalle completo está en `CLAUDE.md` §7**, que es donde hay que
mirar antes de tocar nada relacionado.

| | Estado | Resumen |
|---|---|---|
| **H1** | 🔴 **Abierto** | El "Punto Fijo" automático **es Newton disfrazado**: la g(x) generada es siempre `x − f/f′`, así que el criterio \|g′\|<1 nunca se pone a prueba. No es un error de cálculo; es un problema pedagógico. Sin fase asignada |
| **H2** | 📋 Patrón | **Cuatro veces** el documento o un docstring prometió algo que el código no tenía (`gx_candidates`, `formulas`, la premisa de D4, la cobertura de los tests). Por eso la regla 1: verificar ejecutando antes de construir encima |
| **H3** | 🔴 **Abierto** | **`excel_templates.py` (1091 líneas) no tiene NINGÚN test.** Los "162/162 pasando" cubren métodos y parseo, no el Excel. Quien lo toque trabaja sin red |
| **H4** | ✅ Cerrado | **El más grave de FASE 3: el validador aprobaba una fórmula INCORRECTA** (criterio de Bisección invertido). Un corrector con falsos positivos enseña mal. Incluye la lección de método: "pasa las pruebas" no basta, hay que intentar engañarlo a mano |
| **H5** | ✅ Cerrado | Practicar se quedaba **en blanco y en silencio** ante un 404: `fetch` no rechaza por error HTTP, y el código tomaba el cuerpo por bueno. Auditadas después las 6 llamadas del frontend: ninguna otra lo tenía |
| **H6** | 🟡 Parcial | 12 documentos en `docs/` que `CLAUDE.md` ignoraba, y al menos uno ya contradice el código. Cabecera de aviso puesta; el resto de la decisión, abierta |

---

## 4. Cómo se trabaja en este proyecto

Esto no es burocracia: cada punto viene de algo que salió mal cuando no se hizo.

1. **Verifica contra el código real antes de asumir.** Es la regla 1 de CLAUDE.md y la razón
   de ser de **H2**. Un plan aprobado, un docstring o una frase de este mismo documento **no
   son evidencia**. Ejecuta y mide. Cuatro veces habría costado días construir sobre una
   premisa falsa; verificar costó minutos.
2. **Muestra el diff antes de aplicar** cualquier cambio en un archivo existente, y espera
   confirmación. `CalcularPage.jsx` en particular carga nueve bugs cerrados y verificados en
   vivo (G1–G9): cada cambio ahí se acompaña de su batería de regresión.
3. **No toques el backend sin avisar.** Y en concreto **no toques `excel_templates.py`** sin
   traer tests contigo (H3).
4. **Verifica de verdad, no sólo que compile.** Build y linter no son verificación. Aquí se
   mide en el navegador, se cuentan píxeles del canvas y se intenta romper lo construido a
   propósito. Si algo **no** se puede verificar, se dice explícitamente en vez de suponerlo.
5. **Si una premisa —tuya o del director— no se sostiene al comprobarla, para y regístrala**
   como hallazgo. No sigas construyendo encima. Así salieron H1, H2, H5 y H6.
6. **`CLAUDE.md` se actualiza ANTES de commitear**, en la misma tarea. Si algo no está en
   `CLAUDE.md`, no existe.
7. **Commits separados por unidad de trabajo**, con el mensaje explicando el *porqué* y lo que
   se verificó, no sólo el qué.
8. Antes de commitear documentación: `python scripts/check_chars.py` (regla 6.8).

### Dos trampas del entorno que ya han costado tiempo

- **El dev server puede servir código obsoleto.** Ha pasado tras restaurar un archivo con
  `Copy-Item`: el arreglo estaba en disco y el navegador ejecutaba la versión anterior incluso
  tras recargar. Ante un cambio que "no se ve", comprueba primero que el servidor lo sirve
  (`fetch('/src/…')`) y toca la fecha del fichero si hace falta.
- **Las pruebas de interacción dan falsos negativos.** Tres veces: `mouseleave` (React lo
  sintetiza desde `mouseout`), `focus` (el panel del navegador no tiene el foco del sistema, y
  sin él no se dispara ningún evento) y el búfer viejo de la consola (abre pestaña nueva antes
  de dar por buenos los errores). Antes de declarar un bug de interacción, comprueba que el
  evento **llegó a dispararse**.

### Comandos

```bash
# Frontend
cd frontend && npm run dev            # desarrollo (puerto 5173)
cd frontend && npm run build          # validar build
cd frontend && npx eslint src         # linter

# Backend — DESDE LA RAIZ del repo, los imports son `from backend.X`
uvicorn backend.main:app --port 8000
python -m pytest backend/test         # 162 tests

# Documentación
python scripts/check_chars.py         # caracteres de alfabetos ajenos
```

**Para probar Practicar contra un backend local** hay que repuntar `frontend/src/api.js` a
`http://127.0.0.1:8000` **y devolverlo a Render antes de commitear**. Ya se hizo varias veces
sin incidente, pero es un pie de banco: comprueba `git status` antes de cerrar.
