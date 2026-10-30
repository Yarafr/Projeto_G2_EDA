"""Ordenação por base (radix sort LSD, base 256). O(d · (n + 256))."""


def base(v):
    if not v:
        return []
    menor, maior = min(v), max(v)
    if menor == maior:
        return list(v)
    a = [x - menor for x in v]        # tudo >= 0 (aceita negativos)
    passadas = ((maior - menor).bit_length() + 7) // 8
    for p in range(passadas):
        desloc = 8 * p
        baldes = [[] for _ in range(256)]
        for x in a:                   # distribuição estável por byte
            baldes[(x >> desloc) & 255].append(x)
        a = [x for b in baldes for x in b]
    return [x + menor for x in a]