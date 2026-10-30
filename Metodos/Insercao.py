def insercao_intervalo(a, lo, hi):
    for i in range(lo + 1, hi + 1):
        x = a[i]
        j = i - 1
        while j >= lo and a[j] > x:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = x

def insercao(v):
    a = list(v)
    insercao_intervalo(a, 0, len(a) - 1)
    return a