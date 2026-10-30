def intercalacao(v):
    n = len(v)
    if n <= 1:
        return list(v)
    meio = n // 2
    esq = intercalacao(v[:meio])
    dire = intercalacao(v[meio:])
    saida = []
    i = j = 0
    ne, nd = len(esq), len(dire)
    while i < ne and j < nd:         
        if esq[i] <= dire[j]:        
            saida.append(esq[i])
            i += 1
        else:
            saida.append(dire[j])
            j += 1
    saida.extend(esq[i:])
    saida.extend(dire[j:])
    return saida