# Simulador Ponchon–Savarit

Benceno (1) – tolueno (2), 101.325 kPa. Datos didácticos de la actividad.

## Abrir en Mac, Windows o Linux

Necesitas Python 3.10 o posterior. No requiere paquetes de pip ni conexión a Internet durante su uso.

1. Descomprime el ZIP y abre la carpeta `Ponchon_Savarit`.
2. Abre Terminal dentro de esa carpeta.
3. Ejecuta:

```bash
python3 app.py
```

En Windows puede usarse `py app.py`. Si no se abre el navegador automáticamente, visita http://127.0.0.1:8501 . Mantén la terminal abierta. Detén el programa con Ctrl+C. Si el puerto está ocupado: `python3 app.py --port 8502`.

Si el sistema no reconoce Python, instala Python 3 antes de ejecutar el programa. Abrir `interfaz.html` directamente no ejecuta los cálculos: inicia `app.py`.

## Uso

Modifica F, zF, xD, xB o R y pulsa **Calcular separación**. Presión y estado de alimentación son fijos porque la base de datos corresponde solo a 101.325 kPa y líquido saturado. Activa **Ver puntos de diferencia** para la construcción completa o desactívalo para ampliar las etapas. El control deslizante muestra el trazado progresivo. Los círculos de etapas ofrecen x/y al posar el cursor.

Exporta el resumen como JSON, las etapas como CSV y el diagrama visible como SVG. **Imprimir / guardar PDF** exporta la vista de resultados mediante el navegador. Para incluir todas las etapas en el diagrama, lleva el deslizador al máximo antes de exportar. Los resultados pertenecen a las entradas indicadas al final de la pantalla; después de editar entradas debes recalcular.

## Caso de referencia

F=100 kmol/h; zF=0.40; xD=0.95; xB=0.05; R=2.5.

- D = 38.888889 kmol/h; B = 61.111111 kmol/h; L0 = 97.222222 kmol/h.
- QC = 4,193,743.263889 kJ/h (1,164.928684 kW), calor retirado.
- QR = 4,231,095.847222 kJ/h (1,175.304402 kW), calor suministrado.
- N gráfico = 11.579425; redondeo = 12 etapas teóricas, incluido rehervidor parcial (estimación equivalente a 11 platos + rehervidor).
- Alimentación en etapa 6, contando desde arriba. El condensador total no cuenta.

La última etapa se interpola en composición: no representa un plato físico fraccionario. El redondeo no es una solución exacta de las dos purezas para una columna discreta; no se realiza un ajuste MESH para esa columna de 12 etapas.

## Comprobar resultados

```bash
python3 validacion.py
```

La validación resuelve raíces de balances algebraicos por bisección, sin llamar al trazado por puntos de diferencia. Comprueba los balances de cada plato completo, incluido el de alimentación, cuatro reflujos, escalamiento del flujo y ocho entradas inválidas. Genera `resultados/validacion.json` y `resultados/etapas.csv`.

La independencia es del procedimiento numérico: se usa la misma tabla didáctica. No es validación experimental ni una auditoría de un tercero. Los cierres locales cubren los 11 platos completos trazados; el último paso fraccionario no se verifica como un rehervidor entero a xB.

## Archivos

- `app.py`: servidor local y API.
- `modelo.py`: propiedades, balances, puntos de diferencia y etapas.
- `diagramas.py`: gráfico SVG.
- `interfaz.html`: interfaz, controles y exportaciones.
- `validacion.py`: procedimiento independiente y pruebas.
- `pruebas_integracion.py`: pruebas de la API; ejecutar con `python3 pruebas_integracion.py`.

La comprobación visual completa del navegador queda pendiente en el equipo de uso; el entorno de generación impidió iniciar Chromium. Se verificaron la sintaxis JavaScript, la API y la validez XML de los gráficos SVG.
- `Memoria_tecnica.pdf`: teoría, resultados, validación, límites, IA y referencias.
- `Guion_demostracion.md`: exposición de 6–8 minutos.
- `resultados/`: caso base, etapas, validación y diagramas.

## Alcance

Cp líquido constante; mezcla líquida ideal; sin entalpía de mezclado; sin corrección sensible de vapor; presión constante; sin pérdidas de calor; etapas de equilibrio; condensador total y rehervidor parcial. No estima eficiencia de platos, altura o diámetro de columna, hidráulica ni seguridad industrial. No cambia sistema químico ni presión. Los datos de equilibrio son aproximados y se interpolan linealmente; T se interpola antes de evaluar h.

## Ampliación: componentes y Excel

La interfaz permite comparar dos componentes mediante sus temperaturas normales de ebullición y exportar/importar un libro Excel (.xlsx) con cuatro hojas: Entradas, Balances, Etapas y Procedimiento. La importación actual lee las variables F, zF, xD, xB y R, además de los nombres y temperaturas normales de ebullición.

**Límite importante:** la comparación por temperatura normal de ebullición es un indicador preliminar, no sustituye la volatilidad relativa ni un cálculo de equilibrio a la presión de operación. En esta versión el motor termodinámico sigue siendo el caso validado benceno–tolueno a 101.325 kPa; cambiar los nombres/temperaturas en la ficha no convierte el motor en un simulador universal. Para ampliar a otros pares se requiere incorporar datos VLE y modelos de entalpía apropiados para cada sistema (por ejemplo, Antoine/Raoult para mezclas suficientemente ideales o un modelo de coeficientes de actividad cuando corresponda), además de validarlos.

Para el Excel se instala `openpyxl` mediante `requirements.txt` durante el despliegue.
