#!/usr/bin/env python3
"""Gera tabelas-resumo em Markdown a partir dos CSVs de experimentos,
para colar diretamente na Secao 7 (Resultados) do relatorio."""
import csv
import statistics as st
from collections import defaultdict
from pathlib import Path

REQ = Path("data/experimentos/resultados.csv")
ROUND = Path("data/experimentos/resumo_rounds.csv")
OUT = Path("data/experimentos/tabelas_resumo.md")


def ler_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def resumo_por_config(rows):
    grupos = defaultdict(list)
    for r in rows:
        grupos[(r["configuracao"], r["cenario"])].append(r)
    linhas = []
    for (cfg, cen), rs in sorted(grupos.items()):
        tempos = [num(r["total_duration_s"]) for r in rs if num(r["total_duration_s"]) is not None]
        toks = [num(r["tokens_por_segundo"]) for r in rs if num(r["tokens_por_segundo"]) is not None]
        ttft = [num(r["ttft_proxy_s"]) for r in rs if num(r["ttft_proxy_s"]) is not None]
        erros = sum(1 for r in rs if r.get("erro"))
        linhas.append({
            "configuracao": cfg, "cenario": cen, "n": len(rs),
            "tempo_total_medio_s": round(st.mean(tempos), 3) if tempos else "-",
            "ttft_medio_s": round(st.mean(ttft), 3) if ttft else "-",
            "tokens_s_medio": round(st.mean(toks), 2) if toks else "-",
            "erros": erros,
        })
    return linhas


def main():
    if not REQ.exists() or not ROUND.exists():
        print("Rode antes: python scripts/04_experimentos.py")
        return
    req_rows = ler_csv(REQ)
    round_rows = ler_csv(ROUND)
    resumo = resumo_por_config(req_rows)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("### Tabela 1 - Resumo por configuracao/cenario (media por requisicao)\n\n")
        f.write("| Configuracao | Cenario | N | Tempo total medio (s) | TTFT medio (s) | Tokens/s medio | Erros |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for l in resumo:
            f.write(f"| {l['configuracao']} | {l['cenario']} | {l['n']} | "
                     f"{l['tempo_total_medio_s']} | {l['ttft_medio_s']} | "
                     f"{l['tokens_s_medio']} | {l['erros']} |\n")

        f.write("\n### Tabela 2 - Uso de recursos por round\n\n")
        f.write("| Configuracao | Cenario | Round | Concorrencia | Wall time (s) | CPU (container) | Memoria (container) | Threads |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in round_rows:
            f.write(f"| {r['configuracao']} | {r['cenario']} | {r['round_id']} | "
                     f"{r['concorrencia_alvo']} | {r['wall_time_round_s']} | "
                     f"{r['cpu_pct_ollama']} | {r['mem_uso_ollama']} | {r['threads_ollama']} |\n")

    print(f"Tabelas geradas em {OUT}")


if __name__ == "__main__":
    main()
