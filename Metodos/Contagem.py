MAX_FAIXA_CONTAGEM = 10_000_000


def contagem(v):
    if not v:
        return []
    menor, maior = min(v), max(v)
    k = maior - menor + 1
    if k > MAX_FAIXA_CONTAGEM:
        raise MemoryError(f"faixa {k} excede o teto da contagem")
    cont = [0] * k
    for x in v:
        cont[x - menor] += 1          
    saida = []
    for i, c in enumerate(cont):
        if c:
            saida.extend([i + menor] * c)
    return saida