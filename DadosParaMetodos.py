import random

SEMENTE = 42
_r = random.Random(SEMENTE)

# -------------------------------------------------------------------
CASOS_BORDA = {
    "vazia": [],
    "um_elemento": [7],
    "todos_iguais": [5] * 100,
    "ja_ordenada": list(range(100)),
    "invertida": list(range(100, 0, -1)),
    "negativos": [-3, 5, -10, 0, 2, -1],
    "todos_negativos": [-1, -5, -3, -5, -100],
    "mista": [_r.randint(-50, 50) for _ in range(200)],
    "grande_mista": [_r.randint(-10**6, 10**6) for _ in range(3000)],
}


# --------------------------------------------------------------------
def aleatorio_grande(n=100_000):
    r = random.Random(SEMENTE)
    return [[r.randrange(0, 10**12) for _ in range(n)]]


def faixa_estreita(n=1_000_000):
    r = random.Random(SEMENTE)
    return [[r.randint(0, 100) for _ in range(n)]]


def quase_ordenado(n=200_000):
    r = random.Random(SEMENTE)
    v = list(range(n))
    for _ in range(n // 100):
        i = r.randrange(n - 11)
        j = i + r.randint(1, 10)
        v[i], v[j] = v[j], v[i]
    return [v]


def minuscula(tamanho=20, repeticoes=5000):
    r = random.Random(SEMENTE)
    return [[r.randint(0, 1000) for _ in range(tamanho)]
            for _ in range(repeticoes)]


CENARIOS = {
    "aleatorio_grande": aleatorio_grande,
    "faixa_estreita": faixa_estreita,
    "quase_ordenado": quase_ordenado,
    "minuscula": minuscula,
}


# ----------------------------------------------------------------------
def erro_duas_corridas(n=20_000):
    return [list(range(0, n, 2)) + list(range(1, n, 2))]


def erro_trocas_distantes(n=20_000):
    r = random.Random(SEMENTE)
    v = list(range(n))
    for _ in range(n // 100):
        i, j = r.randrange(n), r.randrange(n)
        v[i], v[j] = v[j], v[i]
    return [v]


def erro_outlier(n=200_000):
    r = random.Random(SEMENTE)
    v = [r.randint(0, 100) for _ in range(n)]
    v[n // 2] = 10**9
    return [v]


EXTRAS = {
    "erro_duas_corridas": erro_duas_corridas,
    "erro_trocas_distantes": erro_trocas_distantes,
    "erro_outlier": erro_outlier,
}