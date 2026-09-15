#!/bin/bash
# Observa processos e threads do container ollama, em repouso e durante uma inferencia.
set -e
mkdir -p data/ps_snapshots

echo "=== Snapshot 1: em repouso (antes da requisicao) ==="
docker exec ollama sh -c 'ps -eo pid,ppid,stat,ni,pri,psr,pcpu,pmem,nlwp,comm --sort=-pcpu' \
  | tee data/ps_snapshots/01_repouso_ps.txt

echo
echo "=== Arvore de processos (pstree -p, se disponivel) ==="
docker exec ollama sh -c 'pstree -p 2>/dev/null || echo "pstree indisponivel; usando ps -ef"; ps -ef' \
  | tee data/ps_snapshots/02_repouso_pstree.txt

echo
echo "=== Disparando requisicao longa em background para observar processos durante a inferencia ==="
curl -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Explique em detalhes, com pelo menos 400 palavras, o funcionamento de escalonadores de processos em sistemas operacionais Linux, cobrindo CFS, prioridades e filas multiníveis.",
  "stream": false
}' > data/ps_snapshots/resposta_longa.json &
CURL_PID=$!

sleep 2
echo "=== Snapshot 2: durante a inferencia (ps -eo ...) ==="
docker exec ollama sh -c 'ps -eo pid,ppid,stat,ni,pri,psr,pcpu,pmem,nlwp,comm --sort=-pcpu' \
  | tee data/ps_snapshots/03_durante_inferencia_ps.txt

echo
echo "=== Snapshot 2b: threads detalhadas (ps -eLf) do processo runner ==="
docker exec ollama sh -c 'ps -eLf | head -60' \
  | tee data/ps_snapshots/04_durante_inferencia_threads.txt

echo
echo "Aguardando termino da requisicao em background..."
wait $CURL_PID
echo "Requisicao concluida. Resposta salva em data/ps_snapshots/resposta_longa.json"

echo
echo "=== docker stats (uso agregado por container, amostra unica) ==="
docker stats --no-stream ollama open-webui | tee data/ps_snapshots/05_docker_stats.txt
