from Metodos.Insercao import insercao
from Metodos.Intercalacao import intercalacao
from Metodos.RapidaComPivoAleatorio import rapida
from Metodos.Hibrida import hibrida
from Metodos.Contagem import contagem, MAX_FAIXA_CONTAGEM
from Metodos.Base import base

METODOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "rapida": rapida,
    "hibrida": hibrida,
    "contagem": contagem,
    "base": base,
}

LIMITE_MINUSCULA = 32      
AMOSTRA = 1000             
FRACAO_QUASE = 0.05        
FATOR_FAIXA = 0.5         
PASSADAS_MAX_BASE = 8     

def escolher(v):
    n = len(v)
    if n <= LIMITE_MINUSCULA:
        return "insercao"

    menor, maior = min(v), max(v)
    if menor == maior:
        return "insercao"                        

    passo = max(1, n // AMOSTRA)
    pares = descidas = 0
    for i in range(passo, n, passo):
        pares += 1
        if v[i - 1] > v[i]:
            descidas += 1
    if descidas <= FRACAO_QUASE * pares:
        return "insercao"                       
    faixa = maior - menor + 1
    if faixa <= FATOR_FAIXA * n and faixa <= MAX_FAIXA_CONTAGEM:
        return "contagem"

    passadas = ((faixa - 1).bit_length() + 7) // 8
    if passadas <= PASSADAS_MAX_BASE:
        return "base"

    return "hibrida"


def ordenar(v):
    return METODOS[escolher(v)](v)