"""Pruebas automáticas: compara el método húngaro con fuerza bruta en matrices aleatorias."""
import random
from itertools import permutations
from hungaro import metodo_hungaro, fuerza_bruta


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


if __name__ == "__main__":
    test_ejemplo_diapositivas()
    test_aleatorias()
    test_rectangular()
    print("Todas las pruebas pasaron.")
