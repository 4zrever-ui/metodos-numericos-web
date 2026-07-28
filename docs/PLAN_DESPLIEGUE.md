# Plan de despliegue del backend — endpoint `/practicar/plantilla`

> **Documento de preparación. Nada de esto se ha ejecutado.**
> Redactado el 2026-07-28 a petición del director, para decidir con datos si se
> despliega y en qué orden.

---

## 1. Qué cambia en el backend

Tres archivos, **todos aditivos**. Ninguna función existente se modifica.

| Archivo | Cambio | Riesgo |
|---|---|---|
| `backend/excel/formula_specs.py` | **NUEVO** (~190 líneas). Sólo lee: importa `to_excel_formula`, que ya existía | Ninguno: nadie más lo importa salvo `main.py` |
| `backend/test/test_formula_specs.py` | **NUEVO** (10 tests). No se ejecuta en producción | Ninguno |
| `backend/main.py` | **+41/−1**: un `import` y el endpoint `POST /practicar/plantilla` | Bajo: ruta nueva, no toca las existentes |

**`excel_templates.py` no se toca** — decisión D2, precisamente porque no tiene tests (H3).

---

## 2. ¿Rompe algo de lo que ya funciona?

**Evidencia recogida, no suposición:**

- **Suite completa: 162/162** (152 previos + 10 nuevos). Los 152 anteriores pasan sin cambios.
- **Los 8 endpoints responden 200** contra el backend con el código nuevo:

```
GET  /                     200        49 bytes
POST /params               200       105 bytes
POST /analyze              200       182 bytes
POST /method/newton        200      1201 bytes
POST /method/biseccion     200      5921 bytes
POST /method/all           200      2858 bytes
POST /excel/single         200      5791 bytes
POST /practicar/plantilla  200      8136 bytes   ← el nuevo
```

- El endpoint nuevo **no comparte estado** con nada: recibe una ecuación, la parsea con el
  mismo `parse_equation` de siempre, y devuelve cadenas. No escribe, no cachea, no muta.

**Reserva honesta:** la cobertura de `main.py` es escasa (2 tests de capa endpoint, de G6).
Que los 8 respondan 200 es un humo bueno, no una garantía de que sus *contenidos* no hayan
cambiado. Lo que sí está fijado por tests es el motor matemático y, ahora, la coincidencia
entre las fórmulas servidas y las plantillas de Excel.

---

## 3. ¿Necesita variables de entorno o dependencias nuevas?

**No, ninguna de las dos.**

- `backend/requirements.txt` **no cambia**. Contiene fastapi, uvicorn, starlette, pydantic,
  sympy, numpy, **openpyxl** y python-multipart, con versiones fijadas.
- `formula_specs.py` importa **sólo** `to_excel_formula`, que ya estaba.
- `openpyxl` sólo lo usa el *test* nuevo (que no corre en producción); el módulo de
  especificación no lo necesita.
- El endpoint no lee ninguna variable de entorno.

---

## 4. Orden de despliegue: ¿qué depende de qué?

| Parte de FASE 3 | ¿Necesita el backend desplegado? |
|---|---|
| Estado del módulo (paso 1) | **No** |
| Motor de celdas (paso 3) | **No** — es cliente puro |
| `FunctionGraph` extraído + tema (pasos 2a/2b) | **No** |
| **Practicar** (pasos 4–6) | **SÍ** |

O sea: **todo lo demás se puede desplegar y usar sin tocar Render.** Sólo Practicar depende.

**Qué se ve hoy si se sube el frontend sin el backend:** Practicar muestra la introducción,
los cuatro ejercicios y el mensaje *"El servidor respondió 404: el backend desplegado todavía
no tiene el endpoint /practicar/plantilla"*. Es correcto y diagnóstico — **pero conviene saber
que hasta hace unas horas no era así**: se quedaba en blanco y en silencio (hallazgo H5, ya
corregido). Si se decide subir sólo el frontend, ese mensaje es lo que verá un visitante.

**¿Se puede probar todo en local indefinidamente?** Sí, sin límite: `uvicorn backend.main:app
--port 8000` y `api.js` apuntando a `127.0.0.1:8000`. Es como se ha verificado todo. La única
pega es que hay que acordarse de devolver `api.js` antes de commitear — ya ha pasado dos veces
sin incidente porque se restauró siempre, pero es un pie de banco que conviene no repetir
muchas veces más.

---

## 5. ¿Render despliega solo al hacer push, o hay que lanzarlo a mano?

> ✅ **RESPONDIDO EMPÍRICAMENTE (2026-07-28): SE DESPLIEGA SOLO.**
> Al pushear los 14 commits de FASE 3, `/practicar/plantilla` pasó de **404 a 200 en menos de
> dos minutos**, **sin que nadie tocara el panel de Render**. Auto-Deploy está activado y el
> servicio construye desde `main`. Vercel desplegó el frontend en la misma ventana.
> Lo que sigue es el razonamiento previo, que quedó confirmado.

**Investigado antes del push. Respuesta corta de entonces: casi con seguridad se despliega
solo, pero no estaba probado — y daba igual, porque el propio push lo respondía sin riesgo.**

### Lo que sí está establecido (medido, no supuesto)

**1. El backend desplegado está AL DÍA con lo pusheado. No hay atraso.**
El último commit pusheado que toca `backend/` es **`87c4f86`** (2026-06-17, arreglo G2+G7).
Sondeando la API en producción, esos arreglos **están vivos**:

```
POST /params  {"equation":"x**3 - 4*x + 1"}
  → roots: [0.2541016884, 1.8608058531, -2.1149075415]   ← G7: las 3 raíces reales
POST /params  {"equation":"x**2 + 1"}
  → roots: []                                            ← G2: sin raíz fantasma
POST /practicar/plantilla
  → 404                                                  ← FASE 3, aún sin pushear
```

O sea: **todo lo pusheado está desplegado, y lo único que falta es lo que todavía no se ha
subido.** No existe ningún commit pusheado que Render no tenga.

**2. Render construye DESDE EL REPOSITORIO.** Lo prueban dos commits del historial hechos
justamente para que el despliegue funcionara: `e4c6cb2` "add requirements.txt para deploy" y
`1c45a7a` "fix python version 3.11". Un servicio que no construyera desde el repo no
necesitaría ninguno de los dos.

### Lo que NO se puede probar desde fuera

**Que Auto-Deploy esté activado.** Es un ajuste del panel, y no hay forma de leerlo por HTTP.
Los servicios de Render conectados a un repositorio lo traen **activado por defecto**, y el
hecho de que no haya atraso encaja con eso — pero también encajaría con que alguien lo
desplegara a mano tras el push de junio. **Las dos hipótesis explican lo observado**, así que
esto es una inferencia, no una comprobación.

### Cómo salir de dudas (dos vías, ninguna arriesgada)

- **La rápida:** panel de Render → *Settings → Build & Deploy → **Auto-Deploy***. Treinta
  segundos. De paso conviene mirar ahí el **Root Directory** y el **Start Command**: los
  imports del proyecto son `from backend.X`, así que el servidor tiene que arrancarse **desde
  la raíz del repositorio** (`uvicorn backend.main:app`), no desde `backend/`. Si hoy funciona,
  ya está bien puesto; sólo es para no asumirlo.
- **La que se responde sola:** **el push lo despeja.** Si tras subir se empieza a responder
  `200` en `/practicar/plantilla` sin que nadie toque nada, es automático. Si sigue dando
  `404` pasados unos minutos, es manual y se lanza desde el panel.

**Por eso esta incógnita NO bloquea la decisión.** El peor caso de equivocarse es que haya que
entrar al panel a darle a un botón, con Practicar mostrando su mensaje de 404 mientras tanto —
que desde el arreglo de H5 es un mensaje claro y no una página muda.

---

## 6. Verificación después de desplegar (lista para ejecutar)

1. **El servicio arranca.** `GET https://metodos-numericos-web.onrender.com/` → 200 con
   `{"mensaje": "API Métodos Numéricos funcionando"}`. Si el arranque falla, Render deja la
   versión anterior sirviendo; se vería en los logs del panel.
2. **Nada de lo viejo se rompió.** Repetir los 7 endpoints previos y comparar con la tabla de
   §2. Especialmente `/method/all` y `/excel/single`, que son los más pesados.
3. **El endpoint nuevo responde.** `POST /practicar/plantilla` con
   `{"equation":"x^3 - 2*x - 5","metodo":"newton"}` → 200 con `hoja.filas` de 7 elementos.
4. **Practicar en vivo**, con `api.js` ya apuntando a Render: cargar los cuatro ejercicios,
   completar la fila de Newton y ver la hoja desplegarse hasta `Convergencia = "SI"`.
5. **Los tres casos que más costaron:** forma equivalente aceptada, signo invertido rechazado,
   y el criterio del intervalo invertido marcado como *"coincide por casualidad"* (H4).
6. **Primera petición lenta.** Render hiberna; la primera llamada tras un rato tarda ~20 s
   (medido hoy: 22.5 s). Practicar **no tiene banner de cold-start** —eso es de la calculadora—
   así que se quedará en "Pidiendo la plantilla del método…" ese tiempo. **No es un fallo, pero
   es una diferencia de trato entre pestañas que quizá quieras igualar.**

---

## 7. Si sale mal

- **Reversión:** `git revert` de los commits de backend y nuevo despliegue. El endpoint es
  aditivo, así que revertirlo sólo lo hace desaparecer; nada más depende de él.
- **Reversión sin tocar el repo:** desde el panel de Render se puede volver a un deploy
  anterior. Es lo más rápido si algo falla en caliente.
- **El frontend no necesita revertirse** aunque el backend se caiga: Practicar mostrará su
  mensaje de 404 y las otras dos pestañas seguirán funcionando con normalidad.

---

## 8. Recomendación

**Un solo push de todo, y comprobar §6 inmediatamente después.**

La pregunta de §5 ya no obliga a decidir por adelantado: lo más probable es que Render se
despliegue solo, y si no lo hace, se ve en dos minutos sondeando `/practicar/plantilla` y se
lanza a mano desde el panel. Mientras tanto Practicar muestra su mensaje de 404, que nombra
exactamente lo que falta.

**Lo único que sí conviene resolver antes del push no es técnico:** la revisión visual de la
hoja sigue pendiente. Desplegar antes de que alguien la haya mirado significa que el primer
par de ojos sobre el diferenciador del proyecto serán los de un visitante.

Y una condición previa que no es técnica: **la revisión visual de la hoja sigue pendiente.**
Desplegar antes de que alguien la haya mirado significa que el primer par de ojos sobre el
diferenciador del proyecto serán los de un visitante.
