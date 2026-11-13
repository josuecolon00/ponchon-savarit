# Presentación y demostración · 6–8 minutos

## 1. Problema y objetivo · 45 segundos

“Separamos una alimentación de 100 kmol/h con 40% molar de benceno. Buscamos 95% de benceno en destilado y 5% en fondos. El simulador usa Ponchon–Savarit para combinar equilibrio, materia y energía.”

Abre `python3 app.py` antes de presentar. Deja el caso obligatorio cargado.

## 2. Modelo termodinámico · 1 minuto

Muestra las dos curvas. Explica que la tabla x–y–T relaciona fases que están en equilibrio: no se deben usar x e y como si fueran iguales. La entalpía de líquido usa la temperatura de burbuja; la de vapor usa las entalpías de los componentes en sus puntos normales de ebullición. La recta de vapor es consecuencia de esa aproximación, no un error de dibujo. No se dispone de Cp del vapor.

## 3. Balances y puntos de diferencia · 1 minuto

Muestra D=38.889, B=61.111 y L0=97.222 kmol/h. Activa “Ver puntos de diferencia”. Explica que DeltaD y DeltaB son puntos auxiliares de balance, no estados físicos de una corriente. El punto de alimentación queda sobre la recta que los une.

QC se retira; QR se suministra. Por eso FhF + QR = DhD + BhB + QC. No se impone flujo molar interno constante.

## 4. Trazado de etapas · 90 segundos

Desactiva la vista completa para ampliar las etapas. Lleva el deslizador a 1: empieza en y1=xD porque el condensador es total. Sigue equilibrio hasta x1 y la recta operativa para obtener y2. Lleva el deslizador a 6 y señala la alimentación. Completa las 12 líneas.

“Se obtienen 11.58 etapas gráficas y se redondea a 12, incluido el rehervidor parcial. El condensador total no cuenta. La fracción es una interpolación gráfica; las purezas exactas en una columna de un número entero de etapas necesitan un ajuste adicional.”

## 5. Cambio en vivo · 1 minuto

Antes de cambiar, pregunta: “Si aumento el reflujo, ¿qué pasará con etapas y energía?”

Cambia R de 2.5 a 3.0 y pulsa calcular. Las etapas gráficas bajan de 11.579 a 10.436, mientras QC sube de 1164.929 a 1331.347 kW y QR de 1175.304 a 1341.723 kW. D y B permanecen iguales porque F y las tres composiciones no cambiaron. Hay una compensación entre energía y cantidad de etapas.

## 6. Validación e IA · 1 minuto

Muestra `resultados/validacion.json` y explica que la segunda ruta usa balances algebraicos y bisección, no las intersecciones del diagrama. Ambas coinciden dentro del redondeo numérico. Se verificaron balances por plato, incluida la alimentación; esto no valida experimentalmente las propiedades.

Explica que ChatGPT apoyó la programación y la documentación. Las decisiones revisadas fueron los signos de calor, las composiciones de cada fase, el cambio de sección y el conteo del rehervidor. No afirmes haber hecho cálculos manuales o pruebas que todavía no hayas reproducido personalmente.

## 7. Cierre · 30 segundos

Como prueba de detección de errores, introduce R=1: aparece reflujo insuficiente. Restaura el caso obligatorio y exporta el resumen y el diagrama.

## Preguntas para prepararte

- ¿Por qué H depende de y y h de x? Cada fase tiene su propia composición.
- ¿Por qué DeltaB tiene entalpía negativa? Es un punto auxiliar hB−QR/B, no una corriente real a temperatura negativa.
- ¿Por qué no usar McCabe–Thiele como igualdad exacta? Su hipótesis habitual de flujos molares constantes difiere de este cálculo energético.
- ¿Qué limita la precisión? Tabla aproximada, interpolación y ausencia de Cp del vapor; etapas ideales y equipos idealizados.
- ¿Qué significa R de pinch? El límite obtenido de la línea de equilibrio en la alimentación; el algoritmo además vigila la secuencia completa para detectar otros problemas.
