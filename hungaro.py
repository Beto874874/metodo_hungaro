"""
Programa de asignación óptima con el método húngaro
Avance 1 — núcleo del algoritmo, modo paso a paso e instancias de prueba

Uso:
    python hungaro.py            -> resuelve las instancias de ejemplo
    python hungaro.py --pasos    -> muestra cada paso del método
"""

import sys
from itertools import permutations

M_GRANDE = 10**9  # costo para asignaciones prohibidas


# ---------------------------------------------------------------------------
# Utilidades de impresión
# ---------------------------------------------------------------------------
def imprimir_matriz(matriz, filas, columnas, titulo="", filas_cub=(), cols_cub=()):
    """Imprime la matriz; marca con * los ceros y con | las líneas que cubren."""
    if titulo:
        print(f"\n  {titulo}")
    ancho = max(6, max(len(str(v)) for fila in matriz for v in fila) + 3)
    encabezado = " " * 10 + "".join(
        (c + ("|" if j in cols_cub else "")).rjust(ancho) for j, c in enumerate(columnas))
    print(encabezado)
    for i, fila in enumerate(matriz):
        marca = "—" if i in filas_cub else " "
        celdas = ""
        for v in fila:
            texto = "M" if v >= M_GRANDE else str(v)
            if v == 0:
                texto += "*"
            celdas += texto.rjust(ancho)
        print(f"  {marca}{filas[i][:7]:<7}{celdas}")


# ---------------------------------------------------------------------------
# Preparación de la matriz
# ---------------------------------------------------------------------------
def balancear(costos, filas, columnas):
    """Si la matriz no es cuadrada, agrega filas o columnas ficticias con costo 0."""
    n_f, n_c = len(costos), len(costos[0])
    matriz = [fila[:] for fila in costos]
    filas, columnas = list(filas), list(columnas)
    if n_f < n_c:
        for k in range(n_c - n_f):
            matriz.append([0] * n_c)
            filas.append(f"Ficticio{k + 1}")
    elif n_c < n_f:
        for fila in matriz:
            fila.extend([0] * (n_f - n_c))
        columnas += [f"Ficticia{k + 1}" for k in range(n_f - n_c)]
    return matriz, filas, columnas


def preparar(costos, maximizar=False):
    """Reemplaza prohibidas (None) por M y convierte maximización en minimización."""
    validos = [v for fila in costos for v in fila if v is not None]
    mayor = max(validos)
    matriz = []
    for fila in costos:
        nueva = []
        for v in fila:
            if v is None:
                nueva.append(M_GRANDE)
            else:
                nueva.append(mayor - v if maximizar else v)
        matriz.append(nueva)
    return matriz


# ---------------------------------------------------------------------------
# Pasos del método
# ---------------------------------------------------------------------------
def reducir_filas(m):
    return [[v - min(fila) for v in fila] for fila in m]


def reducir_columnas(m):
    n = len(m)
    minimos = [min(m[i][j] for i in range(n)) for j in range(n)]
    return [[m[i][j] - minimos[j] for j in range(n)] for i in range(n)]


def emparejamiento_maximo(m):
    """Máximo número de ceros independientes (caminos aumentantes)."""
    n = len(m)
    col_de_fila = [-1] * n
    fila_de_col = [-1] * n

    def intentar(i, visitadas):
        for j in range(n):
            if m[i][j] == 0 and j not in visitadas:
                visitadas.add(j)
                if fila_de_col[j] == -1 or intentar(fila_de_col[j], visitadas):
                    col_de_fila[i] = j
                    fila_de_col[j] = i
                    return True
        return False

    for i in range(n):
        intentar(i, set())
    return col_de_fila, fila_de_col


def cubrir_ceros(m):
    """Mínimo de líneas que cubren todos los ceros (teorema de König).
    Devuelve (filas cubiertas, columnas cubiertas, emparejamiento)."""
    n = len(m)
    col_de_fila, fila_de_col = emparejamiento_maximo(m)
    filas_marcadas = {i for i in range(n) if col_de_fila[i] == -1}
    cols_marcadas = set()
    pendientes = list(filas_marcadas)
    while pendientes:
        i = pendientes.pop()
        for j in range(n):
            if m[i][j] == 0 and j not in cols_marcadas:
                cols_marcadas.add(j)
                k = fila_de_col[j]
                if k != -1 and k not in filas_marcadas:
                    filas_marcadas.add(k)
                    pendientes.append(k)
    filas_cub = set(range(n)) - filas_marcadas
    return filas_cub, cols_marcadas, col_de_fila


def ajustar(m, filas_cub, cols_cub):
    """Resta el menor no cubierto a lo no cubierto y lo suma en los cruces."""
    n = len(m)
    menor = min(m[i][j] for i in range(n) for j in range(n)
                if i not in filas_cub and j not in cols_cub)
    nueva = [fila[:] for fila in m]
    for i in range(n):
        for j in range(n):
            if i not in filas_cub and j not in cols_cub:
                nueva[i][j] -= menor
            elif i in filas_cub and j in cols_cub:
                nueva[i][j] += menor
    return nueva, menor


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def metodo_hungaro(costos, filas, columnas, maximizar=False, mostrar_pasos=False):
    original, filas, columnas = balancear(costos, filas, columnas)
    m, filas, columnas = balancear(preparar(costos, maximizar), filas[:len(costos)],
                                   columnas[:len(costos[0])])
    n = len(m)

    if mostrar_pasos:
        imprimir_matriz(m, filas, columnas, "Matriz de trabajo"
                        + (" (convertida a minimización)" if maximizar else ""))
    m = reducir_filas(m)
    if mostrar_pasos:
        imprimir_matriz(m, filas, columnas, "Paso 2: reducción por filas")
    m = reducir_columnas(m)
    if mostrar_pasos:
        imprimir_matriz(m, filas, columnas, "Paso 3: reducción por columnas")

    iteracion = 1
    while True:
        filas_cub, cols_cub, asignacion = cubrir_ceros(m)
        lineas = len(filas_cub) + len(cols_cub)
        if mostrar_pasos:
            imprimir_matriz(m, filas, columnas,
                            f"Paso 4 (vuelta {iteracion}): {lineas} líneas para n = {n}",
                            filas_cub, cols_cub)
        if lineas == n:
            break
        m, menor = ajustar(m, filas_cub, cols_cub)
        if mostrar_pasos:
            imprimir_matriz(m, filas, columnas,
                            f"Paso 5: ajuste con el menor no cubierto = {menor}")
        iteracion += 1

    resultado = []
    total = 0
    for i, j in enumerate(asignacion):
        if i < len(costos) and j < len(costos[0]):
            costo = original[i][j]
            if costo is None:
                raise ValueError("No existe una asignación sin celdas prohibidas")
            resultado.append((filas[i], columnas[j], costo))
            total += costo
        else:
            resultado.append((filas[i], columnas[j], None))  # queda sin asignar
    return resultado, total


def fuerza_bruta(costos, maximizar=False):
    """Verificación para matrices cuadradas pequeñas: prueba las n! asignaciones."""
    n = len(costos)
    mejor = None
    for p in permutations(range(n)):
        if any(costos[i][p[i]] is None for i in range(n)):
            continue
        total = sum(costos[i][p[i]] for i in range(n))
        if mejor is None or (total > mejor if maximizar else total < mejor):
            mejor = total
    return mejor


def mostrar_resultado(resultado, total, unidad):
    print()
    for agente, tarea, costo in resultado:
        if costo is None:
            print(f"  {agente:<13} -> {tarea:<10} (sin asignar)")
        else:
            print(f"  {agente:<13} -> {tarea:<10} {costo} {unidad}")
    print(f"  {'TOTAL':<27} {total} {unidad}")


# ---------------------------------------------------------------------------
# Instancias de prueba
# ---------------------------------------------------------------------------
INSTANCIAS = [
    {
        "nombre": "1. Operarios y máquinas (minimizar horas) — ejemplo de las diapositivas",
        "filas": ["Ana", "Beto", "Carla", "Dani"],
        "columnas": ["M1", "M2", "M3", "M4"],
        "costos": [[10, 19, 8, 15],
                   [10, 18, 7, 17],
                   [13, 16, 9, 14],
                   [12, 19, 8, 18]],
        "maximizar": False, "unidad": "h",
    },
    {
        "nombre": "2. Vendedores y zonas (maximizar ventas, millones)",
        "filas": ["Laura", "Mateo", "Sofía"],
        "columnas": ["Centro", "Norte", "Sur"],
        "costos": [[12, 9, 7],
                   [8, 11, 10],
                   [10, 7, 12]],
        "maximizar": True, "unidad": "M$",
    },
    {
        "nombre": "3. Repartidores y pedidos (matriz 3x4 + una ruta prohibida, km)",
        "filas": ["Repartidor A", "Repartidor B", "Repartidor C"],
        "columnas": ["P1", "P2", "P3", "P4"],
        "costos": [[4, None, 6, 5],
                   [3, 7, 4, 8],
                   [6, 5, 3, 4]],
        "maximizar": False, "unidad": "km",
    },
]


if __name__ == "__main__":
    pasos = "--pasos" in sys.argv
    for inst in INSTANCIAS:
        print("=" * 70)
        print(inst["nombre"])
        print("=" * 70)
        res, total = metodo_hungaro(inst["costos"], inst["filas"], inst["columnas"],
                                    inst["maximizar"], mostrar_pasos=pasos)
        mostrar_resultado(res, total, inst["unidad"])
        if len(inst["costos"]) == len(inst["costos"][0]):
            fb = fuerza_bruta(inst["costos"], inst["maximizar"])
            print(f"  Verificación por fuerza bruta: {fb} -> "
                  f"{'OK' if fb == total else 'ERROR'}")
        print()
