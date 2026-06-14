# Correcciones Bloque 1 — Métodos Numéricos Web

Tres archivos para reemplazar en `frontend/src/`. Todo verificado: el build de
Vite pasa limpio (0 errores) y cada cambio fue probado contra el backend real.

## Archivos

| Archivo | Acción | Qué hace |
|---|---|---|
| `mathNotation.js` | **NUEVO** — copiar a `frontend/src/` | Normalizador de notación. Convierte LaTeX, Unicode y atajos a notación Python que el backend entiende. |
| `App.jsx` | **REEMPLAZAR** `frontend/src/App.jsx` | Integra el normalizador, arregla el canvas en modo claro, añade retry de cold-start, aviso de raíz exacta y vista previa "interpretado como…". |
| `App.css` | **REEMPLAZAR** `frontend/src/App.css` | Estilos nuevos para la vista previa de notación y el banner de servidor despertando. |

## Instalación

```bash
# Desde la raíz del proyecto
cp App.jsx        frontend/src/App.jsx
cp App.css        frontend/src/App.css
cp mathNotation.js frontend/src/mathNotation.js

cd frontend
npm run build        # debe terminar sin errores
npm run dev          # probar en local
```

No requiere instalar dependencias nuevas. No toca el backend.

## Qué se arregló (verificado)

### 1. Notación de funciones (el bug de la imagen 4)
El campo g(x) y la ecuación ahora aceptan:
- Raíz cúbica: `\sqrt[3]{1-x}`, `∛(1-x)`, `raiz3(1-x)`, `cbrt(1-x)` → todas funcionan
- Raíz cuadrada: `\sqrt{x+2}`, `√(x+2)`
- Exponentes: `x^3`, `x³`, `x**3`
- Fracciones LaTeX: `\frac{1}{x+2}`
- Constantes: `π`, símbolos `·` `×` `÷` `−`

El usuario ve una línea **"Interpretado como: …"** debajo del campo cuando su
entrada se normaliza, para confirmar que el sistema entendió bien.

> **Hallazgo:** la g(x) `cbrt(1-x)` de la imagen 4 sí es válida, pero converge
> *lentamente* (|g'(raíz)| = 0.716), por eso agota las 25 iteraciones. No era
> solo notación: esa g(x) es matemáticamente pobre para esa ecuación. El error
> de parseo lo ocultaba. Ahora el usuario llega al diagnóstico de "no convergió"
> en vez de un error confuso.

### 2. Canvas en modo claro
El gráfico ya no tiene fondo oscuro hardcodeado. Detecta `prefers-color-scheme`
y usa la paleta correcta. Se redibuja solo si cambias el tema del sistema.

### 3. Cold start de Render
La primera consulta tras inactividad reintenta automáticamente (hasta 4 veces,
con backoff) y muestra un banner: *"El servidor está iniciando…"*. Antes daba
"Failed to fetch" sin explicación.

### 4. Raíz exacta (iters = 0)
Cuando x₀ ya es la raíz exacta (ej. `x-1` con x₀=1), en vez de una tabla de una
fila que parece vacía, muestra un aviso claro explicando que convergió en 0
iteraciones porque el punto inicial ya era la solución.

### 5. Descarga de Excel
La g(x) se normaliza antes de enviarse a los endpoints de Excel, evitando los
errores de parseo que rompían la descarga.

## Lo que NO se hizo (a propósito)
- No se instaló MathQuill/MathLive. El normalizador resuelve el 95% del dolor
  sin añadir 200KB de dependencias.
- No se tocó el motor matemático del backend. Está correcto.
