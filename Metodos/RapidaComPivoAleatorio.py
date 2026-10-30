import random

from Metodos.Insercao import insercao_intervalo


def rapida_nucleo(a, lo, hi, limiar=0):
    while lo < hi:
        if hi - lo + 1 <= limiar:
            insercao_intervalo(a, lo, hi)
            return
        p = a[random.randint(lo, hi)]
        lt, i, gt = lo, lo, hi
        while i <= gt:
            x = a[i]
            if x < p:
                a[lt], a[i] = a[i], a[lt]
                lt += 1
                i += 1
            elif x > p:
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
            else:
                i += 1
        if lt - lo < hi - gt:
            rapida_nucleo(a, lo, lt - 1, limiar)
            lo = gt + 1
        else:
            rapida_nucleo(a, gt + 1, hi, limiar)
            hi = lt - 1


def rapida(v):
    a = list(v)
    rapida_nucleo(a, 0, len(a) - 1, 0)
    return a