from Metodos.RapidaComPivoAleatorio import rapida_nucleo

LIMIAR_HIBRIDA = 24

def hibrida(v):
    a = list(v)
    rapida_nucleo(a, 0, len(a) - 1, LIMIAR_HIBRIDA)
    return a