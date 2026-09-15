#!/bin/bash
# Baixa o modelo Llama-3.2-3B-Instruct (GGUF, Q4_K_M) dentro do container ollama.
#
# NOTA IMPORTANTE (documentar no relatorio):
# O model card de referencia no Hugging Face e meta-llama/Llama-3.2-3B-Instruct
# (pesos originais em safetensors, repositorio com acesso restrito por licenca).
# Para a execucao local via Ollama, foi utilizado o build GGUF Q4_K_M distribuido
# pela biblioteca oficial do Ollama (tag "llama3.2:3b"), que corresponde ao mesmo
# modelo-base (familia Llama 3.2, variante Instruct, ~3,21B parametros), apenas
# convertido/quantizado para GGUF Q4_K_M pela propria Ollama. Isso evita a
# necessidade de autenticacao/token do Hugging Face para um repositorio gated,
# mantendo a mesma familia/checkpoint/faixa de parametros registrada.
set -e

echo "Baixando modelo llama3.2:3b (GGUF, Q4_K_M) no container ollama..."
time docker exec ollama ollama pull llama3.2:3b

echo
echo "Modelos disponiveis:"
docker exec ollama ollama list

echo
echo "Espaco ocupado pelo volume de modelos:"
docker exec ollama du -sh /root/.ollama/models 2>/dev/null || true
