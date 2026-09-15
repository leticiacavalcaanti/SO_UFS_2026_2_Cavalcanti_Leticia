#!/usr/bin/env python3
"""Gera os graficos principais (Parte C) a partir de data/experimentos/*.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REQ = Path("data/experimentos/resultados.csv")
OUT_DIR = Path("data/experimentos")


def ler_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def grafico_concorrencia(rows):
    grupos = {"1 requisicao": [], "4 requisicoes (sucesso)": []}
    timeouts = 0
    total_4 = 0
    for r in rows:
        if r["configuracao"] != "config2_concorrencia":
            continue
        if r["cenario"] == "concorrencia_1":
            v = num(r["total_duration_s"])
            if v is not None:
                grupos["1 requisicao"].append(v)
        elif r["cenario"] == "concorrencia_4":
            total_4 += 1
            v = num(r["total_duration_s"])
            if v is not None:
                grupos["4 requisicoes (sucesso)"].append(v)
            else:
                timeouts += 1

    labels = list(grupos.keys())
    medias = [sum(v) / len(v) if v else 0 for v in grupos.values()]

    fig, ax1 = plt.subplots(figsize=(7, 5))
    bars = ax1.bar(labels, medias, color=["#4C78A8", "#E45756"])
    ax1.set_ylabel("Tempo total medio por requisicao (s)")
    ax1.set_title("Config. 2 - Concorrencia: tempo medio e taxa de timeout")
    for b, v in zip(bars, medias):
        ax1.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.1f}s", ha="center")

    taxa_timeout = 100 * timeouts / total_4 if total_4 else 0
    ax1.text(1, medias[1] / 2, f"{taxa_timeout:.0f}% das\nrequisicoes\ncom timeout\n(>300s)",
              ha="center", color="white", fontsize=11, fontweight="bold")

    fig.tight_layout()
    out = OUT_DIR / "grafico_concorrencia.png"
    fig.savefig(out, dpi=150)
    print(f"Salvo: {out}")


def grafico_contexto(rows):
    grupos_tempo = {"num_ctx=2048": [], "num_ctx=8192": []}
    for r in rows:
        if r["configuracao"] != "config3_contexto":
            continue
        chave = "num_ctx=2048" if r["cenario"] == "num_ctx_2048" else "num_ctx=8192"
        v = num(r["total_duration_s"])
        if v is not None:
            grupos_tempo[chave].append(v)

    labels = list(grupos_tempo.keys())
    medias = [sum(v) / len(v) for v in grupos_tempo.values()]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, medias, color=["#54A24B", "#F58518"])
    ax.set_ylabel("Tempo total medio por requisicao (s)")
    ax.set_title("Config. 3 - Contexto: num_ctx=2048 vs 8192")
    for b, v in zip(bars, medias):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{v:.1f}s", ha="center")
    fig.tight_layout()
    out = OUT_DIR / "grafico_contexto.png"
    fig.savefig(out, dpi=150)
    print(f"Salvo: {out}")


def main():
    rows = ler_csv(REQ)
    grafico_concorrencia(rows)
    grafico_contexto(rows)


if __name__ == "__main__":
    main()
