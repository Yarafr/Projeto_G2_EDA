import argparse
import csv
import inspect
import multiprocessing as mp
import os
import random
import statistics
import time

import DadosParaMetodos as D
from Escolhedor import METODOS, ordenar, escolher

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "Resultados_para_Analise")
FUNCOES = dict(METODOS)
FUNCOES["ordenar"] = ordenar
FUNCOES["escolher"] = escolher           # só o custo da decisão
COLS = list(METODOS) + ["ordenar"]


def _cronometrar(f, lote):
    copias = [list(l) for l in lote]     # cópia FORA do cronômetro
    t0 = time.perf_counter()
    for l in copias:
        f(l)
    return time.perf_counter() - t0


def _filho(nome, lote, reps, fila):
    try:
        tempos = [_cronometrar(FUNCOES[nome], lote) for _ in range(reps)]
        fila.put(("ok", statistics.median(tempos)))
    except MemoryError:
        fila.put(("inviavel", None))
    except Exception as e:               # não esconde bugs
        fila.put(("erro:" + repr(e), None))


def medir(nome, lote, reps, timeout):
    fila = mp.Queue()
    p = mp.Process(target=_filho, args=(nome, lote, reps, fila))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return f"timeout(>{timeout:g}s)"
    try:
        status, valor = fila.get(timeout=5)
    except Exception:
        return "erro"
    return valor if status == "ok" else status


def _reduzido(gen):
    p = inspect.signature(gen).parameters
    args = {k: max(1, v.default // 10) for k, v in p.items()
            if k in ("n", "repeticoes")}
    return gen(**args)


# -----------------------------------------------------------
def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _fmt(s):
    x = _num(s)
    return f"{x:.4f}" if x is not None else str(s)


def gerar_tabela(linhas):
    dados, escolheu = {}, {}
    for cen, met, t, esc in linhas:
        dados.setdefault(cen, {})[met] = t
        escolheu[cen] = esc
    out = ["| cenário | " + " | ".join(COLS) + " | melhor | escolher (s) | escolheu |",
           "|" + "---|" * (len(COLS) + 4)]
    pior = {c: 0.0 for c in COLS}
    for cen, d in dados.items():
        nums = {c: _num(d[c]) for c in COLS if _num(d[c]) is not None}
        melhor = min(nums, key=nums.get)
        cel = []
        for c in COLS:
            t = _fmt(d[c])
            cel.append(f"**{t}**" if c == melhor else t)
            if c in nums:
                pior[c] = max(pior[c], nums[c] / nums[melhor])
            else:
                pior[c] = float("inf")
        out.append(f"| {cen} | " + " | ".join(cel) +
                   f" | {melhor} | {_fmt(d['escolher'])} | {escolheu[cen]} |")
    out.append("\n**Pior razão (tempo / melhor do cenário) por método "
               "(timeout ou inviável = infinito):**\n")
    out.append("| " + " | ".join(COLS) + " |")
    out.append("|" + "---|" * len(COLS))
    out.append("| " + " | ".join("inf" if pior[c] == float("inf")
                                 else f"{pior[c]:.2f}x" for c in COLS) + " |")
    return "\n".join(out)


# -------------------------------------------------------
def _t(f, v, reps=5):
    xs = []
    for _ in range(reps):
        c = list(v)
        t0 = time.perf_counter()
        f(c)
        xs.append(time.perf_counter() - t0)
    return statistics.median(xs)


def calibrar():
    import Metodos.Hibrida as H
    from Metodos.Insercao import insercao
    from Metodos.Hibrida import hibrida
    from Metodos.Contagem import contagem
    from Metodos.Base import base
    r = random.Random(1)

    print("1) Inserção vs híbrida (aleatório) -> LIMITE_MINUSCULA")
    for n in (8, 16, 24, 32, 48, 64, 96, 128):
        v = [r.randrange(10**6) for _ in range(n)]
        print(f"   n={n:4d} insercao={_t(insercao, v, 200)*1e6:8.1f}us "
              f"hibrida={_t(hibrida, v, 200)*1e6:8.1f}us")

    print("2) Limiar da híbrida (n=100000) -> LIMIAR_HIBRIDA")
    v = [r.randrange(10**12) for _ in range(100_000)]
    for T in (1, 8, 16, 24, 32, 48, 64):
        H.LIMIAR_HIBRIDA = T
        print(f"   T={T:3d} {_t(hibrida, v, 3):.4f}s")
    H.LIMIAR_HIBRIDA = 24

    print("3) Contagem vs base vs híbrida por faixa (n=200000) -> FATOR_FAIXA")
    n = 200_000
    for k in (100, 1_000, 10_000, 100_000, 800_000, 3_200_000):
        v = [r.randrange(k) for _ in range(n)]
        try:
            tc = f"{_t(contagem, v, 3):.4f}s"
        except MemoryError:
            tc = "inviavel"
        print(f"   faixa={k:8d} contagem={tc} base={_t(base, v, 3):.4f}s "
              f"hibrida={_t(hibrida, v, 3):.4f}s")

    print("4) Base vs híbrida por nº de bits (n=100000) -> PASSADAS_MAX_BASE")
    for bits in (8, 16, 24, 32, 40, 48, 64):
        v = [r.randrange(2**bits) for _ in range(100_000)]
        print(f"   {bits:2d} bits base={_t(base, v, 3):.4f}s "
              f"hibrida={_t(hibrida, v, 3):.4f}s")


# --------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5, help="repetições (mediana)")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="limite total por método, em segundos")
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--extras", action="store_true")
    ap.add_argument("--calibrar", action="store_true")
    a = ap.parse_args()

    if a.calibrar:
        calibrar()
        return

    geradores = dict(D.CENARIOS)
    if a.extras:
        geradores.update(D.EXTRAS)

    os.makedirs(PASTA, exist_ok=True)
    linhas = []
    for nome, gen in geradores.items():
        lote = _reduzido(gen) if a.rapido else gen()
        esc = escolher(lote[0])
        print(f"== {nome} (listas={len(lote)}, n={len(lote[0])}, escolheu={esc})",
              flush=True)
        for fn in FUNCOES:
            t = medir(fn, lote, a.reps, a.timeout)
            linhas.append([nome, fn, t, esc])
            print(f"   {fn:13s} {_fmt(t) + 's' if _num(t) is not None else t}",
                  flush=True)

    with open(os.path.join(PASTA, "resultados.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cenario", "metodo", "mediana_s", "escolheu"])
        w.writerows(linhas)
    tabela = gerar_tabela(linhas)
    with open(os.path.join(PASTA, "tabela.md"), "w", encoding="utf-8") as fh:
        fh.write(tabela + "\n")
    print("\n" + tabela)
    print("\nArquivos gravados em", PASTA)


if __name__ == "__main__":
    main()