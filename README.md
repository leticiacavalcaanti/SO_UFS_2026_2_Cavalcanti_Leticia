# SO_UFS_2026_2_Cavalcanti_Leticia

Atividade 1 (AV1) — Sistemas Operacionais — **Processos, Threads, Escalonamento e Inferência Local com Ollama**
Modalidade individual | Discente: **Leticia Cavalcanti** | 2026.2

## Vídeo da atividade
URL: ver [VIDEO.md](VIDEO.md)

## Trilha e modelo selecionados
- **Trilha A — Chat local: Ollama + Open WebUI**
- **Modelo:** Llama-3.2-3B-Instruct (família Llama 3.2, variante Instruct, ~3,21B parâmetros)
  - Model card de referência: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
  - Formato/quantização executados localmente: GGUF, Q4_K_M (build oficial da biblioteca Ollama, tag `llama3.2:3b` — ver nota abaixo)
  - Licença: Llama 3.2 Community License

> **Nota sobre proveniência do artefato GGUF:** o repositório `meta-llama/Llama-3.2-3B-Instruct` no Hugging Face é *gated* e distribui os pesos originais em `safetensors`. Para execução local via Ollama, foi utilizado o build GGUF Q4_K_M da biblioteca oficial do Ollama (`ollama pull llama3.2:3b`), que corresponde ao mesmo modelo-base (família, checkpoint/variante e faixa de parâmetros). Essa escolha evita a necessidade de token/autenticação do Hugging Face para um repositório restrito, mantendo a mesma identidade de modelo-base declarada no registro da atividade.

## Ambiente de execução
- **Host:** Windows 11, com **Docker Desktop** (backend WSL2) como orquestrador.
- **Ambiente Linux observado:** containers Linux (`ollama` e `open-webui`) executados sobre a VM Linux do Docker Desktop/WSL2 — ou seja, execução **em contêiner**, uma das modalidades previstas no enunciado.
- **GPU:** nenhuma GPU NVIDIA disponível; execução 100% em CPU.
- Detalhes completos (kernel, CPU, RAM, storage, versões) em [data/ambiente_inventario.txt](data/ambiente_inventario.txt), gerado pelo script `scripts/00_inventario_ambiente.sh`.

## Arquitetura simplificada
```
[Navegador] -> http://localhost:3000 -> [container open-webui] -> http://ollama:11434 -> [container ollama] -> [runner llama.cpp / modelo llama3.2:3b]
```
- **Open WebUI** (`ghcr.io/open-webui/open-webui:main`): interface web de chat, porta `3000` (mapeada para `8080` no container).
- **Ollama** (`ollama/ollama:latest`): runtime de inferência, expõe API HTTP local na porta `11434`.
- Comunicação entre camadas via API HTTP local (`OLLAMA_BASE_URL=http://ollama:11434`), conforme exigido no enunciado.
- Volumes Docker nomeados (`ollama_data`, `openwebui_data`) garantem persistência de modelos, índices e conversas entre reinicializações.

## Como reproduzir

### Pré-requisitos
- Docker Desktop instalado e em execução (Windows, com backend WSL2).
- `git`, `curl` e `python3` disponíveis no host para os scripts auxiliares.

### 1. Subir o ambiente
```bash
docker compose up -d
```

### 2. Baixar o modelo
```bash
bash scripts/01_baixar_modelo.sh
```

### 3. Usar a interface web
Acesse http://localhost:3000, crie uma conta local (armazenada apenas no container) e converse com o modelo `llama3.2:3b`.

### 4. Coletar evidências de processos, threads e chamadas de sistema
```bash
bash scripts/00_inventario_ambiente.sh
bash scripts/02_processos_threads.sh
bash scripts/03_strace_syscalls.sh
```

### 5. Rodar os experimentos comparativos (Parte C)
```bash
python scripts/04_experimentos.py
```
Gera `data/experimentos/resultados.csv` (uma linha por requisição) e `data/experimentos/resumo_rounds.csv` (uma linha por rodada, com uso de CPU/memória/threads do container).

### 6. Gerar relatório e slides em PDF
```bash
pip install markdown
python scripts/06_gerar_pdf.py        # gera report/relatorio.pdf
python scripts/07_gerar_slides_pdf.py # gera report/apresentacao.pdf
```

### 7. Encerrar o ambiente
```bash
docker compose down
```
(os volumes `ollama_data`/`openwebui_data` preservam o modelo baixado para a próxima execução; use `docker compose down -v` para remover tudo, incluindo o modelo.)

## Estrutura do repositório
```
.
├── docker-compose.yml
├── scripts/
│   ├── 00_inventario_ambiente.sh
│   ├── 01_baixar_modelo.sh
│   ├── 02_processos_threads.sh
│   ├── 03_strace_syscalls.sh
│   └── 04_experimentos.py
├── data/                     # evidências e resultados brutos gerados pelos scripts
│   ├── ambiente_inventario.txt
│   ├── ps_snapshots/
│   ├── strace/
│   └── experimentos/
├── report/
│   ├── relatorio.md           # relatório técnico (fonte)
│   ├── relatorio.pdf          # relatório técnico exportado (entregável)
│   ├── apresentacao.md        # slides (fonte)
│   ├── apresentacao.pdf       # slides exportados (entregável)
│   └── roteiro_video.md       # roteiro cronometrado para gravação do vídeo
├── declaracao_uso_ia.md
├── declaracao_uso_ia.pdf      # anexo citado no relatório (Seção 11 e questão 26)
├── VIDEO.md
└── README.md
```

## Declaração de Uso de IA Generativa
Ver [declaracao_uso_ia.md](declaracao_uso_ia.md) (anexada ao relatório também em [declaracao_uso_ia.pdf](declaracao_uso_ia.pdf)).

## Licença e observações
Este repositório não contém pesos de modelo, chaves, tokens ou dados pessoais (ver `.gitignore`). O modelo é baixado localmente pelo script `scripts/01_baixar_modelo.sh` a partir da biblioteca oficial do Ollama.
