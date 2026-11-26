# Juan Alberto Trujillo Herrera y Martín Camilo Corredor Pescador

## Asignación óptima con el método húngaro

Programa en Python que resuelve problemas de asignación (agentes → tareas),
minimizando costos o maximizando beneficios. No necesita librerías externas
(Python 3.8 o superior).

### Idea del método húngaro

Para una matriz cuadrada de costos el algoritmo:

1. Resta el mínimo de cada fila y después el mínimo de cada columna; eso no cambia
   qué asignación es óptima pero crea ceros.
2. Busca el mayor número de ceros independientes (uno por fila y por columna).
3. Si no se puede llegar a `n` ceros independientes, calcula el mínimo número de
   líneas que cubren todos los ceros (teorema de König), resta el menor valor no
   cubierto y lo suma en los cruces de las líneas cubrientes.
4. Repite hasta completar `n` ceros independientes: ahí está la asignación óptima.

Para **maximizar**, cada valor se transforma en `mayor_valor - valor` y se resuelve
como minimización. Las asignaciones prohibidas se representan con un costo muy
grande (`10**9`) y las matrices rectangulares se completan con agentes/tareas
ficticias de costo 0 (que aparecen como "sin asignar").

## Cómo ejecutarlo

```bash
python hungaro.py                                     # 3 instancias de ejemplo
python hungaro.py --pasos                             # muestra cada paso del método
python hungaro.py --csv ejemplo.csv                   # minimiza (por defecto)
python hungaro.py --csv ejemplo.csv --objetivo max --unidad 'M$'
python hungaro.py --csv ejemplo_prohibidas.csv --unidad km --pasos
python hungaro.py --menu                              # menú interactivo
python test_hungaro.py                                # pruebas automáticas
```

Opciones de la línea de comandos:

| Opción | Significado |
|--------|-------------|
| `--csv ARCHIVO` | lee la matriz desde un CSV |
| `--menu` | menú para elegir CSV o entrada por teclado |
| `--objetivo min\|max` | minimizar (por defecto) o maximizar |
| `--unidad TEXTO` | unidad que se muestra con los resultados (`h`, `km`, `'M$'`, ...) |
| `--pasos` | imprime las matrices intermedias del algoritmo |

En el menú (`--menu`) se elige la fuente de datos, se pregunta si se quiere
minimizar o maximizar, se introducen (opcionalmente) los nombres de agentes y
tareas y se decide si se muestran los pasos. Todo se vuelve a preguntar cuando la
entrada no es válida: el programa no se detiene con un error de Python.

## Formato del CSV

- La primera fila es el encabezado: **una celda vacía** y luego los nombres de las
  tareas.
- Cada fila siguiente lleva el nombre del agente y sus costos, uno por tarea.
- Una celda **vacía** o con **`X`** (también `x`) marca una asignación prohibida;
  internamente se convierte en `None`.
- Se pueden usar comas o punto y coma como separador; con punto y coma también se
  aceptan decimales con coma (`1,5`).
- Las filas en blanco se ignoran. Si se dejan nombres vacíos se usan `A1`, `A2`,
  `T1`, `T2`, etc.

Ejemplo (`ejemplo_prohibidas.csv`, 3 repartidores y 4 pedidos; la ruta P2 del
repartidor A está prohibida):

```csv
,P1,P2,P3,P4
Repartidor A,4,X,6,5
Repartidor B,3,7,4,8
Repartidor C,6,5,3,4
```

```bash
python hungaro.py --csv ejemplo_prohibidas.csv --unidad km
```

### Validación de la entrada

Se muestran mensajes claros y se termina con código de salida 1 (sin traza de
Python) en estos casos: archivo inexistente o vacío, encabezado sin tareas, filas
con distinto número de columnas, valores no numéricos, todas las celdas
prohibidas o ninguna asignación posible que respete las prohibiciones.

## Resultados de las instancias de ejemplo

| # | Caso | Tipo | Asignación óptima | Total |
|---|------|------|-------------------|-------|
| 1 | 4 operarios × 4 máquinas (horas) | Minimizar | Ana→M4 (15), Beto→M1 (10), Carla→M2 (16), Dani→M3 (8) | **49 h** |
| 2 | 3 vendedores × 3 zonas (ventas, millones) | Maximizar | Laura→Centro (12), Mateo→Norte (11), Sofía→Sur (12) | **35 M$** |
| 3 | 3 repartidores × 4 pedidos, una ruta prohibida (km) | Minimizar, rectangular | A→P4 (5), B→P1 (3), C→P3 (3), agente ficticio→P2 (sin asignar) | **11 km** |

Los casos 1 y 2 se verifican además contra `fuerza_bruta` (que prueba todas las
permutaciones) y las pruebas automáticas comparan ambas implementaciones en 300
matrices aleatorias, incluida la maximización.

## Orden del repositorio

`.gitignore` excluye `__pycache__/`, los archivos `*.pyc`, entornos virtuales,
carpetas de build y cachés de pruebas. El archivo `__pycache__/hungaro.cpython-315.pyc`
ya estaba versionado en un commit anterior; para dejar de seguirlo **sin borrarlo
del disco** hay que quitarlo del índice de Git:

```bash
git rm --cached __pycache__/hungaro.cpython-315.pyc
git add .gitignore README.md hungaro.py entrada.py test_hungaro.py ejemplo.csv ejemplo_prohibidas.csv
git commit -m "Agrega entrada CSV y consola, y limpia archivos generados"
git push
```

`--cached` solo afecta al índice: el `.pyc` sigue en la carpeta local, pero deja
de subirse en futuros commits y `.gitignore` evita que vuelva a aparecer. Si hay
más archivos generados, se puede usar `git rm --cached -r __pycache__/`.
