# Roteiro do vídeo (alvo: 9 min — máximo 10 min)

Grave com câmera/rosto visível no início (identificação) e tela compartilhada no restante.
Use `report/apresentacao.pdf` como apoio visual (pode deixar aberto e ir passando).

## 0:00–0:45 — Identificação e trilha (fala + rosto)
"Meu nome é Leticia Cavalcanti, esta é a Atividade 1 de Sistemas Operacionais, trilha A —
Ollama com Open WebUI — usando o modelo Llama-3.2-3B-Instruct, quantização GGUF Q4_K_M."

## 0:45–2:00 — Ambiente e arquitetura (slide 2 e 3)
- Mostrar `docker compose ps` rodando (containers `ollama` e `open-webui`)
- Explicar: Windows + Docker Desktop (WSL2) como ambiente Linux; sem GPU, execução em CPU
- Mostrar rapidamente `data/ambiente_inventario.txt` (kernel, CPU, RAM)
- Explicar arquitetura: navegador → Open WebUI (:3000) → API HTTP → Ollama (:11434) → llama-server

## 2:00–3:30 — Demonstração ao vivo
- Abrir http://localhost:3000 no navegador, mandar uma pergunta curta ao modelo
- Enquanto gera, abrir um terminal e rodar `docker exec ollama ps -eo pid,ppid,nlwp,pcpu,comm --sort=-pcpu`
  para mostrar o processo `llama-server` aparecendo em tempo real

## 3:30–5:00 — Processos, threads e chamadas de sistema (slides 4 e 5)
- Mostrar `data/ps_snapshots/03_durante_inferencia_ps.txt` e `04_durante_inferencia_threads.txt`
- Explicar: `ollama serve` (PID 1, 25 threads) é o processo supervisor; `llama-server` é criado
  sob demanda como processo filho para a inferência
- Mostrar `data/strace/strace-resumo.txt`: destacar `futex` (72,8% do tempo) e explicar que é
  sincronização entre threads

## 5:00–7:30 — Resultados dos experimentos (slides 6, 7 e 8)
- Mostrar `data/experimentos/tabelas_resumo.md` (ou as tabelas do relatório)
- Destacar o achado principal: concorrência=4 causou 75% de timeout e saturação de CPU
  (55–75% de uso, contra <1% sequencial) — mostrar o gráfico/tabela
- Destacar o efeito do contexto (`num_ctx` 2048 vs 8192): +21% tempo, +30% memória, e o
  recarregamento do modelo ao trocar o contexto

## 7:30–8:30 — Limites, riscos e decisões (slides 9 e 10)
- Sem GPU: não foi possível comparar CPU x GPU
- Ambiente em container/WSL2 pode introduzir ruído nos tempos absolutos
- Decisão de usar `llama3.2:3b` (biblioteca Ollama) em vez do repositório gated do HF — mesmo
  modelo-base, evita autenticação

## 8:30–9:00 — Conclusão
"Concluindo, a responsividade de um sistema local de IA generativa depende menos do tamanho do
modelo e mais da configuração de execução — concorrência e contexto — que interage diretamente
com o escalonamento do sistema operacional. Repositório e demais evidências estão no GitHub,
link na descrição."

---
### Checklist antes de gravar
- [ ] `docker compose up -d` rodando (containers saudáveis)
- [ ] Terminal com `data/` acessível para mostrar os arquivos
- [ ] `report/apresentacao.pdf` aberto como apoio visual
- [ ] Cronômetro visível para não passar de 10 minutos
