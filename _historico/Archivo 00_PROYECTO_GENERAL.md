

# Analiza detalladamente el archivo Excel adjunto y considéralo la fuente de verdad absoluta. En caso de conflicto entre esta especificación y el archivo Excel, prevalece la lógica, estructura y fórmulas contenidas en el archivo ExcelPROYECTO: Plataforma Web Académica para Métodos Numéricos con Exportación Dinámica a Excel

## Objetivo General

Desarrollar una aplicación web académica y profesional para resolver ecuaciones mediante múltiples métodos numéricos. La plataforma debe permitir que el usuario introduzca una ecuación matemática y que el sistema genere automáticamente el desarrollo completo de cada método, mostrando todas las iteraciones, cálculos intermedios, errores y resultados finales.

El objetivo principal es replicar fielmente la estructura, lógica matemática, formato y comportamiento de mis archivos Excel académicos existentes, evitando simplificaciones y preservando la metodología de enseñanza universitaria.

---

# Requisito Fundamental

La aplicación NO debe comportarse como una calculadora que únicamente muestra resultados.

La aplicación debe comportarse como un sistema académico de resolución paso a paso, donde cada método muestre:

- Datos de entrada.
- Parámetros utilizados.
- Fórmulas aplicadas.
- Tabla completa de iteraciones.
- Error absoluto.
- Error relativo.
- Criterios de convergencia.
- Resultado final.
- Interpretación matemática.

---

# Entrada de Ecuaciones

El usuario debe poder ingresar ecuaciones mediante:

Formato texto:

x^3 - 4x + 1 = 0

Formato matemático:

f(x)=x^3-4x+1

Formato LaTeX:

x^{3}-4x+1=0

La aplicación debe validar automáticamente la sintaxis antes de ejecutar cualquier método.

Debe existir una vista previa matemática renderizada.

---

# Métodos Numéricos

La plataforma debe implementar todos los métodos contenidos en mis archivos Excel originales.

Cada método debe funcionar de manera independiente.

La arquitectura debe permitir agregar nuevos métodos en el futuro sin modificar el núcleo de la aplicación.

---

# Detección Automática de Aplicabilidad

La aplicación debe analizar la ecuación ingresada y determinar automáticamente:

- Si el método es aplicable.
- Si el método no es aplicable.
- La razón matemática.

Ejemplos:

✓ Método aplicable

o

✗ Método no aplicable porque no existe cambio de signo en el intervalo seleccionado.

---

# Generación Automática de Parámetros

La aplicación debe intentar generar automáticamente parámetros válidos para cada método.

Entre ellos:

- Intervalos [a,b]
- Aproximaciones iniciales
- Dos aproximaciones iniciales
- Tolerancia
- Número máximo de iteraciones
- Error permitido
- Función g(x)

Prioridad de selección:

1. Enteros positivos.
2. Enteros positivos incluyendo cero.
3. Enteros negativos.
4. Decimales únicamente cuando sea matemáticamente necesario.

Evitar valores arbitrarios o excesivamente complejos.

---

# Generación Inteligente de g(x)

Para los métodos que requieran g(x):

La aplicación debe generar automáticamente múltiples formas algebraicamente equivalentes de g(x).

Debe evaluar:

|g'(x)|

y seleccionar la función con mejor probabilidad de convergencia.

Debe mostrar:

- Todas las alternativas encontradas.
- La alternativa seleccionada.
- La justificación matemática.

---

# Visualización de Resultados

Cada método debe presentar:

- Nombre del método.
- Fundamento matemático.
- Fórmula utilizada.
- Datos iniciales.
- Tabla completa.
- Error por iteración.
- Convergencia.
- Resultado final.

La visualización debe ser clara y académica.

---

# Gráficas

Generar automáticamente:

1. Aproximación vs Iteración.
2. Error vs Iteración.
3. Convergencia del método.
4. Representación de la función.
5. Localización visual de la raíz.

Las gráficas deben actualizarse dinámicamente.

---

# Comparación de Métodos

Generar una tabla comparativa global.

Columnas sugeridas:

- Método
- Raíz aproximada
- Número de iteraciones
- Error final
- Tiempo de ejecución
- Convergencia

Esto permitirá comparar la eficiencia de cada método.

---

# Exportación a Excel

Este punto es CRÍTICO.

Los archivos Excel exportados NO deben contener únicamente valores calculados.

Todos los cálculos deben conservarse mediante fórmulas nativas de Microsoft Excel.

---

# Requisito Obligatorio sobre Fórmulas

Al abrir el archivo Excel:

Los resultados deben verse normalmente.

Pero al seleccionar una celda calculada debe visualizarse la fórmula correspondiente en la barra de fórmulas.

Ejemplo:

Visualmente:

Resultado = 1.234567

Internamente:

=B5-(C5/D5)

o

=POTENCIA(B5,3)-4*B5+1

Las fórmulas deben permanecer editables.

---

# Prohibiciones

NO generar:

- Valores estáticos pegados.
- Capturas de tablas.
- Simulaciones visuales de Excel.
- Datos precalculados sin fórmulas.

NO convertir fórmulas en texto.

NO reemplazar fórmulas por números.

---

# Referencias Dinámicas

Las fórmulas deben utilizar referencias reales de Excel.

Correcto:

=(B5+C5)/2

Incorrecto:

=(2+3)/2

El archivo debe recalcularse automáticamente si el usuario modifica cualquier dato.

---

# Recalculo Automático

Si el usuario modifica:

- La ecuación.
- El intervalo.
- La tolerancia.
- Los valores iniciales.

Todas las iteraciones deben recalcularse automáticamente usando únicamente las fórmulas internas del libro Excel.

---

# Exportación Individual

Cada método debe poder descargarse individualmente.

Ejemplos:

- Bisección.xlsx
- NewtonRaphson.xlsx
- Secante.xlsx

---

# Exportación Global

Debe existir un botón:

"Descargar Todos"

que genere un único archivo Excel.

Cada método debe almacenarse en una hoja independiente.

Ejemplo:

Hoja 1: Bisección

Hoja 2: Falsa Posición

Hoja 3: Punto Fijo

Hoja 4: Newton-Raphson

etc.

---

# Replicación Exacta de Plantillas

La aplicación debe analizar mis archivos Excel originales y utilizarlos como plantillas maestras.

Debe conservar:

- Colores.
- Bordes.
- Tipografías.
- Formatos numéricos.
- Estructura.
- Distribución de columnas.
- Encabezados.
- Celdas combinadas.
- Fórmulas.
- Estilo visual.

El objetivo es que el Excel generado sea prácticamente indistinguible del modelo original.

---

# Tecnologías Recomendadas

Frontend:

- React
- Next.js
- TypeScript
- Tailwind CSS
- MathLive
- KaTeX

Backend:

- Python
- FastAPI

Motor matemático:

- SymPy
- NumPy
- SciPy

Excel:

- OpenPyXL
- XlsxWriter

Gráficas:

- Plotly
- Recharts

---

# Calidad del Código

El proyecto debe seguir principios:

- SOLID
- Clean Architecture
- Componentes reutilizables
- Separación estricta entre interfaz y lógica matemática
- Código documentado
- Escalable
- Mantenible

---

# Resultado Esperado

Quiero una aplicación académica profesional que replique fielmente mis plantillas Excel de métodos numéricos, genere automáticamente los parámetros necesarios, muestre el desarrollo completo de cada método, produzca gráficos de convergencia y permita exportar archivos Excel totalmente funcionales con fórmulas nativas editables y recalculables.