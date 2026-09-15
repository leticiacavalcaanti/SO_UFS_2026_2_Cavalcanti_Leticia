#!/bin/bash
# Anexa strace ao processo "ollama serve" (PID 1 no container) durante uma
# requisicao controlada, e produz um resumo de chamadas de sistema por familia.
set -e
mkdir -p data/strace
export MSYS_NO_PATHCONV=1  # evita que o Git Bash/MSYS converta "/tmp/..." em um caminho do Windows

echo "Instalando strace no container (se necessario)..."
docker exec -u root ollama sh -c '
  if ! command -v strace >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq strace >/dev/null
  fi
  strace --version | head -1
'

echo
echo "Anexando strace ao processo 1 (ollama serve), com -f (segue forks/threads)..."
docker exec ollama sh -c 'strace -f -c -p 1 -o /tmp/strace-resumo.txt' &
STRACE_BG=$!

sleep 2
echo "Disparando requisicao controlada ao Ollama..."
curl -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Explique brevemente o que e um processo em sistemas operacionais.",
  "stream": false
}' > /dev/null

sleep 3
echo "Encerrando strace (SIGINT) para gerar o resumo..."
docker exec ollama sh -c 'kill -2 $(pgrep -f "strace -f -c -p 1")' 2>/dev/null || true
sleep 2

docker exec ollama cat /tmp/strace-resumo.txt > data/strace/strace-resumo.txt 2>&1 || \
  echo "AVISO: nao foi possivel copiar o resumo do strace (verifique permissoes/PID 1 dentro do container)." | tee data/strace/strace-resumo.txt

echo
echo "Resumo salvo em data/strace/strace-resumo.txt"
cat data/strace/strace-resumo.txt
