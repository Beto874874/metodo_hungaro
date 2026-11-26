"""Lectura y validación de la matriz de costos.

Fuentes soportadas: archivo CSV o entrada por consola.
Una celda vacía o con ``X`` significa "asignación prohibida" y se convierte
en ``None`` antes de llamar al método húngaro.
"""

import csv
import math


def parsear_celda(texto):
    """Convierte una celda en número (int/float) o en None si está prohibida."""
    valor = texto.strip()
    if valor == "" or valor.upper() == "X":
        return None
    try:
        numero = float(valor.replace(",", "."))
    except ValueError:
        raise ValueError(
            f"{valor!r} no es un número; use un número, 'X' o deje la celda vacía"
        ) from None
    if not math.isfinite(numero):
        raise ValueError(f"{valor!r} no es un número finito")
    return int(numero) if numero.is_integer() else numero


def validar_matriz(costos, filas, columnas):
    """Comprueba que la matriz sea no vacía, rectangular y resoluble."""
    if not costos or not costos[0]:
        raise ValueError(
            "La matriz de costos está vacía: se necesita al menos un agente y una tarea"
        )
    n_columnas = len(costos[0])
    for i, fila in enumerate(costos, start=1):
        if len(fila) != n_columnas:
            raise ValueError(
                f"La fila {i} tiene {len(fila)} costos, pero la primera tiene "
                f"{n_columnas}; todas las filas deben tener la misma longitud"
            )
    if len(filas) != len(costos) or len(columnas) != n_columnas:
        raise ValueError("El número de nombres no coincide con el tamaño de la matriz")
    if all(celda is None for fila in costos for celda in fila):
        raise ValueError(
            "Todas las celdas están prohibidas (vacías o 'X'); no hay costos para resolver"
        )
    return costos, list(filas), list(columnas)


def leer_csv(ruta):
    """Lee un CSV con encabezado de tareas y una fila por agente.

    Primera fila: celda vacía seguida de los nombres de las tareas.
    Filas siguientes: nombre del agente seguido de sus costos.
    Devuelve (costos, filas, columnas).
    """
    try:
        with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
            lineas = [linea for linea in archivo if linea.strip()]
    except OSError as exc:
        raise ValueError(
            f"No se pudo leer el archivo {ruta!r}: {exc.strerror or exc}"
        ) from exc

    if not lineas:
        raise ValueError(
            "El CSV está vacío; debe tener una fila de encabezado y al menos una fila de costos"
        )

    delimitador = ";" if lineas[0].count(";") > lineas[0].count(",") else ","
    filas_csv = list(csv.reader(lineas, delimiter=delimitador))
    cabecera = filas_csv[0]
    if len(cabecera) < 2:
        raise ValueError(
            "La primera fila del CSV debe tener una celda vacía y los nombres de las tareas"
        )

    columnas = [celda.strip() or f"T{j + 1}" for j, celda in enumerate(cabecera[1:])]
    esperadas = len(columnas) + 1  # nombre del agente + una celda por tarea
    costos = []
    nombres = []
    for i, fila_csv in enumerate(filas_csv[1:], start=2):
        if len(fila_csv) != esperadas:
            raise ValueError(
                f"Fila {i} del CSV: tiene {len(fila_csv)} columnas, se esperaban "
                f"{esperadas} (nombre del agente + una columna por tarea)"
            )
        nombres.append(fila_csv[0].strip() or f"A{len(nombres) + 1}")
        fila_costos = []
        for j, texto in enumerate(fila_csv[1:]):
            try:
                fila_costos.append(parsear_celda(texto))
            except ValueError as exc:
                raise ValueError(f"Fila {i}, columna {j + 2} ({columnas[j]}): {exc}") from exc
        costos.append(fila_costos)

    return validar_matriz(costos, nombres, columnas)


def pedir_entero(mensaje):
    """Pide un entero positivo; vuelve a preguntar si la entrada no es válida."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
            if valor < 1:
                raise ValueError
            return valor
        except ValueError:
            print("  Error: escriba un número entero mayor que 0.")


def pedir_objetivo():
    """Pregunta si se quiere minimizar o maximizar; devuelve un booleano."""
    while True:
        texto = input("¿Minimizar o maximizar? (min/max) [min]: ").strip().lower()
        if texto in ("", "min", "minimizar", "minimum", "minimize"):
            return False
        if texto in ("max", "maximizar", "maximum", "maximize"):
            return True
        print("  Error: escriba 'min' o 'max'.")


def pedir_nombres(cantidad, tipo, prefijo):
    """Pide nombres separados por comas o usa nombres automáticos."""
    texto = input(
        f"Nombres de {tipo} separados por comas "
        f"(Enter para usar {prefijo}1, {prefijo}2, ...): "
    ).strip()
    automaticos = [f"{prefijo}{i + 1}" for i in range(cantidad)]
    if not texto:
        return automaticos
    nombres = [pedazo.strip() for pedazo in texto.split(",")]
    if len(nombres) != cantidad or any(nombre == "" for nombre in nombres):
        print(f"  Aviso: se esperaban {cantidad} nombres; se usarán los predeterminados.")
        return automaticos
    return nombres


def leer_consola():
    """Pide la matriz por teclado. Devuelve (costos, filas, columnas, maximizar)."""
    print("\nEntrada manual de datos")
    n_filas = pedir_entero("Número de agentes (filas): ")
    n_columnas = pedir_entero("Número de tareas (columnas): ")
    maximizar = pedir_objetivo()
    filas = pedir_nombres(n_filas, "agentes", "A")
    columnas = pedir_nombres(n_columnas, "tareas", "T")

    print("Escriba los costos de cada fila separados por comas.")
    print("Use X o deje una celda vacía para marcar una asignación prohibida.")
    costos = []
    for nombre in filas:
        while True:
            texto = input(f"  {nombre}: ").strip()
            partes = texto.split(",")
            if len(partes) != n_columnas:
                print(
                    f"  Error: se esperaban {n_columnas} valores, se recibieron {len(partes)}."
                )
                continue
            try:
                fila = [parsear_celda(parte) for parte in partes]
            except ValueError as exc:
                print(f"  Error: {exc}")
                continue
            costos.append(fila)
            break

    validar_matriz(costos, filas, columnas)
    return costos, filas, columnas, maximizar
