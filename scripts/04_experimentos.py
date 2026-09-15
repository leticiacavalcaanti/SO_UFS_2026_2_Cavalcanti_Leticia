#!/usr/bin/env python3
"""
Experimentos comparativos (Parte C do enunciado) para a Trilha A
(Ollama + Open WebUI), modelo llama3.2:3b (GGUF, Q4_K_M).

Executa 3 configuracoes, cobrindo pelo menos 2 tamanhos de entrada e pelo
menos 2 repeticoes por cenario, totalizando >= 12 execucoes mensuraveis:

  Config 1 - Execucao padrao:
      prompt curto x prompt longo, 2 repeticoes cada (4 execucoes)
  Config 2 - Concorrencia controlada:
      1 requisicao por vez x 4 requisicoes simultaneas, prompt longo,
      2 repeticoes cada (4 rounds; 1 + 4 requisicoes por round)
  Config 3 - Ajuste de execucao local (contexto curto x longo):
      num_ctx=2048 x num_ctx=8192, prompt longo, 2 repeticoes cada (4 execucoes)

Resultados sao gravados em data/experimentos/resultados.csv (uma linha por
requisicao individual) e um resumo por round em
data/experimentos/resumo_rounds.csv.
"""
import concurrent.futures
import csv
import json
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

PROMPT_CURTO = "Explique em uma frase o que e um processo em sistemas operacionais."
PROMPT_LONGO = (
    "Explique em detalhes, com pelo menos 300 palavras, o funcionamento de "
    "escalonadores de processos em sistemas operacionais Linux, cobrindo o "
    "Completely Fair Scheduler (CFS), prioridades, filas multiniveis e a "
    "diferenca entre processos e threads em termos de escalonamento."
)

OUT_DIR = Path("data/experimentos")
OUT_DIR.mkdir(parents=True, exist_ok=True)
CSV_REQ = OUT_DIR / "resultados.csv"
CSV_ROUND = OUT_DIR / "resumo_rounds.csv"

FIELDS_REQ = [
    "timestamp", "configuracao", "cenario", "round_id", "tamanho_entrada",
    "repeticao", "concorrencia_alvo", "num_ctx", "total_duration_s",
    "load_duration_s", "ttft_proxy_s", "prompt_eval_count", "eval_count",
    "tokens_por_segundo", "qualidade", "erro",
]
FIELDS_ROUND = [
    "timestamp", "configuracao", "cenario", "round_id", "concorrencia_alvo",
    "wall_time_round_s", "cpu_pct_ollama", "mem_uso_ollama", "threads_ollama",
    "num_processos_container",
]


def chamar_ollama(prompt, options=None):
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    if options:
        payload["options"] = options
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=data, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"erro": str(e), "wall_s": time.time() - t0}
    return body


def metrics_from_response(body):
    if "erro" in body:
        return {
            "total_duration_s": "", "load_duration_s": "", "ttft_proxy_s": "",
            "prompt_eval_count": "", "eval_count": "", "tokens_por_segundo": "",
            "qualidade": "ERRO", "erro": body["erro"],
        }
    total_ns = body.get("total_duration", 0)
    load_ns = body.get("load_duration", 0)
    prompt_eval_ns = body.get("prompt_eval_duration", 0)
    eval_ns = body.get("eval_duration", 0)
    eval_count = body.get("eval_count", 0)
    tokens_s = (eval_count / (eval_ns / 1e9)) if eval_ns else 0
    resposta = body.get("response", "")
    qualidade = "OK" if len(resposta.strip()) > 30 else "INCOMPLETA"
    return {
        "total_duration_s": round(total_ns / 1e9, 4),
        "load_duration_s": round(load_ns / 1e9, 4),
        "ttft_proxy_s": round((load_ns + prompt_eval_ns) / 1e9, 4),
        "prompt_eval_count": body.get("prompt_eval_count", ""),
        "eval_count": eval_count,
        "tokens_por_segundo": round(tokens_s, 2),
        "qualidade": qualidade,
        "erro": "",
    }


def snapshot_recursos():
    try:
        out = subprocess.run(
            ["docker", "stats", "--no-stream", "--format",
             "{{.CPUPerc}};{{.MemUsage}}", "ollama"],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        cpu, mem = (out.split(";") + ["", ""])[:2]
    except Exception:
        cpu, mem = "", ""
    try:
        threads = subprocess.run(
            ["docker", "exec", "ollama", "sh", "-c",
             "ps -eo nlwp --no-headers | awk '{s+=$1} END {print s}'"],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
    except Exception:
        threads = ""
    try:
        nprocs = subprocess.run(
            ["docker", "exec", "ollama", "sh", "-c", "ps -e --no-headers | wc -l"],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
    except Exception:
        nprocs = ""
    return cpu, mem, threads, nprocs


def write_header_if_needed(path, fields):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def append_row(path, fields, row):
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writerow(row)


def run_single(configuracao, cenario, round_id, tamanho_entrada, repeticao,
                concorrencia_alvo, prompt, num_ctx=None):
    options = {"num_ctx": num_ctx} if num_ctx else None
    body = chamar_ollama(prompt, options)
    m = metrics_from_response(body)
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "configuracao": configuracao, "cenario": cenario, "round_id": round_id,
        "tamanho_entrada": tamanho_entrada, "repeticao": repeticao,
        "concorrencia_alvo": concorrencia_alvo, "num_ctx": num_ctx or "default",
        **m,
    }
    append_row(CSV_REQ, FIELDS_REQ, row)
    return row


def run_round(configuracao, cenario, round_id, concorrencia_alvo, prompt,
              tamanho_entrada, repeticao, num_ctx=None):
    t0 = time.time()
    if concorrencia_alvo <= 1:
        run_single(configuracao, cenario, round_id, tamanho_entrada, repeticao,
                   concorrencia_alvo, prompt, num_ctx)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concorrencia_alvo) as ex:
            futs = [
                ex.submit(run_single, configuracao, cenario, round_id,
                          tamanho_entrada, repeticao, concorrencia_alvo, prompt, num_ctx)
                for _ in range(concorrencia_alvo)
            ]
            concurrent.futures.wait(futs)
    wall = round(time.time() - t0, 3)
    cpu, mem, threads, nprocs = snapshot_recursos()
    append_row(CSV_ROUND, FIELDS_ROUND, {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "configuracao": configuracao, "cenario": cenario, "round_id": round_id,
        "concorrencia_alvo": concorrencia_alvo, "wall_time_round_s": wall,
        "cpu_pct_ollama": cpu, "mem_uso_ollama": mem, "threads_ollama": threads,
        "num_processos_container": nprocs,
    })
    print(f"[{configuracao}] {cenario} round={round_id} concorrencia={concorrencia_alvo} "
          f"wall={wall}s cpu={cpu} mem={mem} threads={threads}")


def main():
    write_header_if_needed(CSV_REQ, FIELDS_REQ)
    write_header_if_needed(CSV_ROUND, FIELDS_ROUND)
    rid = 0

    # ---- Config 1: execucao padrao ----
    for tamanho, prompt in [("curto", PROMPT_CURTO), ("longo", PROMPT_LONGO)]:
        for rep in (1, 2):
            rid += 1
            run_round("config1_padrao", f"padrao_{tamanho}", rid, 1, prompt, tamanho, rep)

    # ---- Config 2: concorrencia controlada (prompt longo) ----
    for concorrencia in (1, 4):
        for rep in (1, 2):
            rid += 1
            run_round("config2_concorrencia", f"concorrencia_{concorrencia}", rid,
                       concorrencia, PROMPT_LONGO, "longo", rep)

    # ---- Config 3: contexto curto x longo (prompt longo) ----
    for ctx in (2048, 8192):
        for rep in (1, 2):
            rid += 1
            run_round("config3_contexto", f"num_ctx_{ctx}", rid, 1, PROMPT_LONGO,
                       "longo", rep, num_ctx=ctx)

    print(f"\nConcluido: {rid} rounds executados.")
    print(f"Resultados por requisicao: {CSV_REQ}")
    print(f"Resumo por round: {CSV_ROUND}")


if __name__ == "__main__":
    main()
