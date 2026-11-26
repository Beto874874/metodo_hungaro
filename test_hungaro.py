"""Pruebas automáticas: algoritmo, lectura de CSV y validación de entrada."""
import os
import random
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from itertools import permutations

from entrada import leer_csv, parsear_celda, validar_matriz
from hungaro import main, metodo_hungaro, fuerza_bruta


def test_ejemplo_diapositivas():
    costos = [[10, 19, 8, 15], [10, 18, 7, 17], [13, 16, 9, 14], [12, 19, 8, 18]]
    _, total = metodo_hungaro(costos, list("ABCD"), list("1234"))
    assert total == 49


def test_aleatorias(veces=300):
    random.seed(7)
    for _ in range(veces):
        n = random.randint(1, 6)
        costos = [[random.randint(0, 30) for _ in range(n)] for _ in range(n)]
        maximizar = random.random() < 0.5
        _, total = metodo_hungaro(costos, [str(i) for i in range(n)],
                                  [str(j) for j in range(n)], maximizar)
        assert total == fuerza_bruta(costos, maximizar), costos


def test_rectangular():
    costos = [[4, 6, 5, 9], [3, 4, 8, 2]]  # 2 agentes, 4 tareas
    _, total = metodo_hungaro(costos, ["A", "B"], list("1234"))
    mejor = min(costos[0][a] + costos[1][b]
                for a, b in permutations(range(4), 2))
    assert total == mejor


def _csv_temporal(contenido):
    archivo = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".csv", delete=False, newline=""
    )
    archivo.write(contenido)
    archivo.close()
    return archivo.name


def test_parsear_celda():
    assert parsear_celda("X") is None
    assert parsear_celda(" x ") is None
    assert parsear_celda("") is None
    assert parsear_celda(" 7 ") == 7
    assert parsear_celda("2.5") == 2.5
    try:
        parsear_celda("hola")
    except ValueError as exc:
        assert "hola" in str(exc)
    else:
        raise AssertionError("un valor no numérico debería dar error")


def test_leer_csv():
    ruta = _csv_temporal(",T1,T2,T3\nA,4,X,6\nB,3,7,\n")
    try:
        costos, filas, columnas = leer_csv(ruta)
        assert filas == ["A", "B"]
        assert columnas == ["T1", "T2", "T3"]
        assert costos == [[4, None, 6], [3, 7, None]]
    finally:
        os.remove(ruta)


def test_leer_csv_con_punto_y_coma():
    ruta = _csv_temporal(";T1;T2\nA;1,5;4\nB;3;2\n")
    try:
        costos, _, columnas = leer_csv(ruta)
        assert costos[0][0] == 1.5
        assert columnas == ["T1", "T2"]
    finally:
        os.remove(ruta)


def test_errores_de_entrada():
    casos = [
        ("", "vacío"),
        (",T1\nA,1,2\n", "columnas"),
        (",T1,T2\nA,hola,2\n", "número"),
        (",T1\nA,X\nB,X\n", "prohibidas"),
    ]
    for contenido, fragmento in casos:
        ruta = _csv_temporal(contenido)
        try:
            try:
                leer_csv(ruta)
            except ValueError as exc:
                assert fragmento in str(exc).lower(), str(exc)
            else:
                raise AssertionError(f"se esperaba error para {contenido!r}")
        finally:
            os.remove(ruta)
    try:
        validar_matriz([[1, 2], [3]], ["A", "B"], ["T1", "T2"])
    except ValueError as exc:
        assert "misma longitud" in str(exc)
    else:
        raise AssertionError("filas de distinto largo deberían dar error")


def test_cli_csv():
    ruta = _csv_temporal(",T1,T2\nA,1,4\nB,3,2\n")
    try:
        salida = StringIO()
        with redirect_stdout(salida):
            codigo = main(["--csv", ruta, "--objetivo", "min", "--unidad", "h"])
        assert codigo == 0
        assert "TOTAL" in salida.getvalue()
        assert "OK" in salida.getvalue()
        errores = StringIO()
        with redirect_stderr(errores):
            codigo = main(["--csv", ruta + ".inexistente"])
        assert codigo == 1
        assert "No se pudo leer" in errores.getvalue()
    finally:
        os.remove(ruta)


if __name__ == "__main__":
    test_ejemplo_diapositivas()
    test_aleatorias()
    test_rectangular()
    test_parsear_celda()
    test_leer_csv()
    test_leer_csv_con_punto_y_coma()
    test_errores_de_entrada()
    test_cli_csv()
    print("Todas las pruebas pasaron.")
