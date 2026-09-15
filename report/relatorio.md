# Relatório Técnico — Atividade 1 (AV1) de Sistemas Operacionais
## Processos, Threads, Escalonamento e Inferência Local com Ollama

**Discente:** Leticia Cavalcanti
**Modalidade:** Individual
**Trilha:** A — Chat local: Ollama + Open WebUI
**Modelo:** Llama-3.2-3B-Instruct (GGUF, Q4_K_M)
**Repositório:** _(preencher com a URL do GitHub, ex.: https://github.com/<usuario>/SO_UFS_2026_2_Cavalcanti_Leticia)_
**Vídeo da atividade:** _(preencher — ver VIDEO.md)_
**Data:** 2026-09-15

---

## 1. Introdução e problema

Aplicações de IA generativa executadas localmente mobilizam processos, threads, memória,
armazenamento, comunicação em rede, arquivos, logs, bibliotecas, runtimes e mecanismos de
proteção do sistema operacional. Este relatório documenta a instalação, execução e análise
experimental de um sistema local de IA generativa baseado em **Ollama** com a interface
**Open WebUI** (Trilha A), relacionando conceitos de Sistemas Operacionais — processos, threads,
chamadas de sistema e escalonamento — ao comportamento observado.

**Pergunta norteadora:** como a camada de aplicação, o modelo de linguagem, a quantidade de
parâmetros, a quantização e a configuração de execução afetam processos, threads, uso de CPU,
memória, armazenamento e responsividade de um sistema local de IA generativa?

## 2. Trilha e modelo

- **Trilha escolhida:** A — Ollama + Open WebUI.
- **Modelo:** Llama-3.2-3B-Instruct, família Llama 3.2, variante Instruct, ~3,21 bilhões de
  parâmetros, formato GGUF, quantização Q4_K_M, licença Llama 3.2 Community License.
- **Model card:** https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
- **Justificativa:** modelo de porte reduzido (dentro do limite de 10B parâmetros), o que
  permite instalação e execução mais rápidas em ambiente local via Ollama. A quantização
  Q4_K_M reduz o consumo de memória e armazenamento sem comprometer significativamente a
  qualidade das respostas, facilitando a coleta de métricas de processos, threads, uso de
  CPU/memória e chamadas de sistema exigidas na Trilha A.
- **Nota de proveniência:** ver observação no [README.md](../README.md) sobre a diferença entre
  o model card original (safetensors, gated) e o artefato GGUF Q4_K_M efetivamente executado
  (biblioteca oficial do Ollama, tag `llama3.2:3b`).

## 3. Ambiente experimental

_(preencher com o conteúdo real de `data/ambiente_inventario.txt` após rodar
`scripts/00_inventario_ambiente.sh`: distribuição/versão do Linux do container, kernel, CPU,
núcleos, RAM, armazenamento, versão do Ollama, tipo de ambiente.)_

Resumo esperado:
- Tipo de ambiente: contêiner Docker (backend WSL2 do Docker Desktop), sem GPU.
- CPUs alocadas ao Docker Desktop: 4 (host Windows 11).
- RAM alocada ao Docker Desktop: ~5,8 GiB.

## 4. Arquitetura

Ver diagrama e descrição em [README.md](../README.md#arquitetura-simplificada).

## 5. Processos, threads e chamadas de sistema

### 5.1 Processos e threads
_(preencher com base em `data/ps_snapshots/*.txt`, gerados por `scripts/02_processos_threads.sh`)_

- Processo principal observado: `ollama` (PID 1 no container, `ollama serve`).
- Processo(s) auxiliar(es) observado(s) durante a inferência: processo "runner" do llama.cpp,
  filho do processo principal, responsável por carregar os pesos e executar a inferência.
- PID/PPID, estado (`STAT`), número de threads (`NLWP`) e uso de CPU/memória: ver tabelas em
  `data/ps_snapshots/01_repouso_ps.txt` (repouso) e
  `data/ps_snapshots/03_durante_inferencia_ps.txt` (durante inferência).
- Comparação repouso x inferência: _(descrever o aumento de CPU%/threads observado)_

### 5.2 Chamadas de sistema
_(preencher com base em `data/strace/strace-resumo.txt`, gerado por
`scripts/03_strace_syscalls.sh`)_

Analisar pelo menos três famílias de chamadas relevantes, por exemplo:
- **Arquivos/memória-mapeada** (`openat`, `mmap`, `read`, `close`): leitura dos pesos do modelo
  (arquivo GGUF) e de arquivos de configuração/log.
- **Memória** (`mmap`, `mprotect`, `brk`): alocação de memória para os buffers do modelo e do
  contexto de inferência.
- **Rede** (`socket`, `accept`, `recvfrom`, `sendto`, `epoll_wait`): atendimento da API HTTP
  local na porta 11434 e comunicação com o Open WebUI.
- **Processos/threads** (`clone`, `futex`, `sched_yield`): criação de threads de trabalho do
  runtime de inferência e sincronização entre elas.

## 6. Metodologia dos experimentos

Foram executadas 12 rodadas mensuráveis, cobrindo três configurações, pelo menos dois tamanhos
de entrada (prompt curto e prompt longo) e pelo menos duas repetições por cenário, conforme
`scripts/04_experimentos.py`:

- **Configuração 1 — execução padrão:** prompt curto x longo, 2 repetições cada (4 execuções),
  requisições sequenciais, `num_ctx` padrão.
- **Configuração 2 — concorrência controlada:** prompt longo, comparando 1 requisição por vez
  x 4 requisições simultâneas, 2 repetições cada (4 rounds; 1+4 requisições por round).
- **Configuração 3 — ajuste de execução local (contexto):** prompt longo, comparando
  `num_ctx=2048` x `num_ctx=8192`, 2 repetições cada (4 execuções).

Métricas coletadas por requisição (via campos da própria API do Ollama, ver
[documentação oficial](https://github.com/ollama/ollama/blob/main/docs/api.md)):
tempo total (`total_duration`), tempo de carregamento do modelo (`load_duration`), TTFT
aproximado (`load_duration + prompt_eval_duration`), tokens/segundo
(`eval_count / eval_duration`), além de uso de CPU/memória do container (`docker stats`) e
número de threads (`ps -eo nlwp`) por round.

## 7. Resultados

_(preencher com tabelas/gráficos a partir de `data/experimentos/resultados.csv` e
`resumo_rounds.csv`. Sugestão de tabelas: tempo total médio por configuração; tokens/s por
configuração; uso de CPU/memória/threads por round; gráfico de barras comparando as três
configurações.)_

## 8. Discussão

_(discutir: efeito da concorrência na responsividade/vazão e nos custos de CPU/memória; efeito
do tamanho de contexto no tempo e no uso de memória; eventuais erros/timeouts observados;
qualidade das respostas.)_

## 9. Relação com Sistemas Operacionais e IA generativa

O runtime do Ollama ilustra, na prática, conceitos centrais de Sistemas Operacionais: um
processo principal que atende requisições via sockets TCP (chamadas `socket`/`accept`/`epoll`),
um processo/thread "runner" responsável pela inferência (criado via `clone`, comunicando-se por
memória mapeada e sincronizado com `futex`), escalonamento cooperativo das threads de inferência
pelo CFS do kernel Linux, e uso de `mmap` para carregar o arquivo de pesos GGUF sem duplicar todo
o conteúdo em memória residente. A execução em contêiner acrescenta uma camada de isolamento de
namespaces e cgroups, que limita e contabiliza os recursos (CPU, memória) usados pelo processo
Ollama, visível via `docker stats`.

## 10. Limitações

- Execução 100% em CPU (sem GPU disponível no host), o que restringe a comparação CPU/GPU
  prevista como uma das variações possíveis da Configuração 3.
- Ambiente virtualizado (Docker Desktop sobre WSL2) introduz uma camada adicional de
  virtualização em relação a uma instalação nativa Linux, podendo afetar levemente medições de
  tempo absoluto (embora não a análise qualitativa de processos/threads/syscalls).
- Amostra de 12 execuções é o mínimo exigido; variações de carga do host Windows durante os
  testes podem introduzir ruído nas medições de tempo.

## 11. Declaração de uso de IA

Ver [declaracao_uso_ia.md](../declaracao_uso_ia.md).

## 12. Conclusão

_(preencher: retomar a pergunta norteadora e responder com base nos resultados obtidos.)_

## 13. Respostas às questões de análise (Seção 9 do enunciado)

**16. Por que a trilha escolhida é adequada à disciplina?**
A Trilha A expõe de forma direta processos e threads distintos (Ollama e Open WebUI),
comunicação via API HTTP local (sockets), execução em contêiner (namespaces/cgroups) e
persistência via volumes — cobrindo múltiplos tópicos centrais de Sistemas Operacionais em um
cenário real de IA generativa.

**17. Qual modelo foi selecionado, quais são seus parâmetros e por que foi escolhido?**
Ver Seção 2.

**18. Como formato, quantização, contexto e tamanho afetaram armazenamento, RAM ou VRAM?**
_(preencher com dados reais de espaço ocupado — `scripts/01_baixar_modelo.sh` imprime o
tamanho do diretório de modelos — e uso de memória por configuração de `num_ctx`.)_

**19. Quais processos e threads foram observados na inicialização e na inferência?**
Ver Seção 5.1.

**20. Quais chamadas de sistema foram relevantes para carga, leitura de dados, comunicação ou logs?**
Ver Seção 5.2.

**21. O aumento de concorrência melhorou responsividade ou vazão? Quais custos surgiram?**
_(preencher com base na Configuração 2 — comparar wall time, tokens/s agregados e uso de
CPU/memória entre concorrência=1 e concorrência=4.)_

**22. Houve competição por CPU, memória, armazenamento, GPU ou rede?**
_(preencher — observar `cpu_pct_ollama`/`mem_uso_ollama` em `resumo_rounds.csv` durante os
rounds de concorrência=4.)_

**23. Como entradas ou contextos maiores afetaram desempenho e recursos?**
_(preencher com base na Configuração 3 — comparar `num_ctx=2048` x `num_ctx=8192`.)_

**24. Como a arquitetura local contribui para privacidade, disponibilidade e controle de dados?**
Por rodar inteiramente em containers locais, sem chamadas a APIs externas, os dados de
conversas e documentos não saem da máquina da discente; a aplicação também continua funcional
offline (após o download do modelo), sem depender de disponibilidade de um provedor remoto.

**25. Quais limitações ameaçam a validade dos resultados?**
Ver Seção 10.

**26. Quais informações geradas por IA precisaram ser verificadas, corrigidas ou rejeitadas?**
Ver [declaracao_uso_ia.md](../declaracao_uso_ia.md).

## 14. Referências

- SILBERSCHATZ, Abraham; GALVIN, Peter B.; GAGNE, Greg. *Operating System Concepts*. 10. ed.
  Hoboken: Wiley, 2018.
- TANENBAUM, Andrew S.; BOS, Herbert. *Modern Operating Systems*. 5. ed. Boston: Pearson, 2023.
- KERRISK, Michael. *The Linux Programming Interface*. San Francisco: No Starch Press, 2010.
- LINUX MAN-PAGES PROJECT. fork(2), execve(2), wait(2), clone(2), pthreads(7), sched(7).
  Disponível em: https://man7.org/linux/man-pages/.
- THE LINUX KERNEL DOCUMENTATION. *Scheduler documentation*. Disponível em:
  https://docs.kernel.org/scheduler/.
- OLLAMA. Repositório oficial e documentação da API. Disponível em:
  https://github.com/ollama/ollama.
- OPEN WEBUI. Repositório oficial. Disponível em: https://github.com/open-webui/open-webui.
- HUGGING FACE. Models. Disponível em: https://huggingface.co/models.
- NIST. *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence
  Profile*. NIST AI 600-1, 2024. Disponível em: https://doi.org/10.6028/NIST.AI.600-1.

**URL do vídeo:** _(preencher — ver VIDEO.md)_
