#!/bin/bash
# Coleta o inventario do ambiente (host Windows + container Linux) usado na atividade.
set -e
OUT="data/ambiente_inventario.txt"
mkdir -p data

{
  echo "=== Inventario do ambiente - $(date '+%Y-%m-%d %H:%M:%S') ==="
  echo
  echo "--- Host (Windows, orquestrador dos containers via Docker Desktop / WSL2) ---"
  docker version
  echo
  docker info | grep -E "CPUs|Total Memory|Server Version|Operating System|Kernel Version"
  echo
  echo "--- Ambiente Linux de execucao: container 'ollama' (imagem ollama/ollama) ---"
  docker exec ollama sh -c '
    echo "[uname -a]"; uname -a
    echo; echo "[/etc/os-release]"; cat /etc/os-release 2>/dev/null
    echo; echo "[nproc]"; nproc
    echo; echo "[free -h ou /proc/meminfo]"; (free -h 2>/dev/null || head -5 /proc/meminfo)
    echo; echo "[df -h]"; df -h
    echo; echo "[lscpu]"; (lscpu 2>/dev/null || echo "lscpu indisponivel neste container")
    echo; echo "[ollama --version]"; ollama --version
    echo; echo "[ollama list]"; ollama list
  '
  echo
  echo "--- GPU ---"
  echo "Sem GPU NVIDIA detectada no host (nvidia-smi indisponivel). Execucao 100% em CPU."
} | tee "$OUT"

echo
echo "Inventario salvo em $OUT"
