# Declaração de Uso de IA Generativa

## Ferramenta e modelo utilizados
Claude Code (Anthropic), modelo Claude Sonnet 5, utilizado via CLI/extensão integrada ao editor.

## Finalidade de cada uso
1. Apoiar a estruturação do repositório (organização de pastas, `docker-compose.yml`, scripts de automação de experimentos e coleta de métricas).
2. Redigir scripts de observação de processos/threads (`ps`, `pstree`, `docker stats`) e de chamadas de sistema (`strace`) a serem executados no container Linux do Ollama.
3. Redigir um script Python para automatizar as 12+ execuções comparativas das Configurações 1, 2 e 3 e gravar métricas em CSV.
4. Auxiliar na redação da estrutura do README, do relatório técnico e desta própria declaração.
5. Explicar conceitos de Sistemas Operacionais (escalonamento, threads, chamadas de sistema) usados na interpretação dos resultados.

## Prompts relevantes (até 5)
1. "Preciso de ajuda com esse trabalho de Sistemas Operacionais sobre Ollama, processos, threads e escalonamento — pode me ajudar?"
2. "Crie o projeto em C:\Users\letic\Documents" (organização do repositório na pasta correta).
3. Definição da trilha, modelo e ambiente: Trilha A (Ollama + Open WebUI), modelo `Llama-3.2-3B-Instruct` (GGUF, Q4_K_M), ambiente WSL/Docker Desktop.
4. Pedido de scripts para inventário do ambiente, observação de processos/threads, `strace` e experimentos comparativos (Configurações 1, 2 e 3).
5. Pedido de estrutura do relatório técnico, README e checklist de entregáveis conforme o enunciado da atividade.

## Sugestões aproveitadas, corrigidas ou rejeitadas
- **Aproveitado:** uso de containers Docker (backend WSL2 do Docker Desktop) como "ambiente Linux", em vez de instalar uma distribuição WSL completa — mais rápido de configurar sem perda de validade, já que a Trilha A prevê explicitamente análise de "execução nativa ou em contêiner".
- **Corrigido/ajustado:** o *model card* de referência no Hugging Face (`meta-llama/Llama-3.2-3B-Instruct`) é um repositório com acesso restrito (*gated*) em formato *safetensors*; para a execução local, foi utilizado o build GGUF Q4_K_M distribuído pela biblioteca oficial do Ollama (`llama3.2:3b`), correspondente ao mesmo modelo-base. Essa diferença foi documentada explicitamente no relatório para preservar a rastreabilidade.
- **Verificado manualmente, não apenas aceito:** todos os comandos de coleta (`ps`, `docker stats`, `strace`, chamadas à API do Ollama) foram efetivamente executados no ambiente da discente, e os números apresentados no relatório vêm dos arquivos `data/*.txt` e `data/experimentos/*.csv` gerados por essas execuções reais — não foram inventados pela IA.

## Erros encontrados
- O script de `strace` sugerido inicialmente pela IA falhou com `ptrace(PTRACE_SEIZE, 1):
  Operation not permitted`, porque containers Docker não concedem `ptrace` por padrão. Corrigido
  adicionando `cap_add: [SYS_PTRACE]` ao serviço `ollama` no `docker-compose.yml`.
- Depois de corrigir a permissão, o `strace` ainda falhava ao copiar o arquivo de resumo
  (`/tmp/strace-resumo.txt`) porque o Git Bash/MSYS no Windows converte automaticamente caminhos
  no estilo `/tmp/...` passados como argumento de linha de comando para um caminho do sistema de
  arquivos Windows. Corrigido definindo `MSYS_NO_PATHCONV=1` no script.
- Nos experimentos de concorrência (Configuração 2, concorrência=4), 6 das 8 requisições
  disparadas em paralelo estouraram o timeout de 300s definido no script Python — não foi um
  erro do script, mas um resultado real e esperado dado que o host tem apenas 4 CPUs e nenhuma
  GPU; esse comportamento foi mantido e discutido no relatório em vez de ser "escondido"
  aumentando artificialmente o timeout.

## Testes, documentação ou observações usados para verificar respostas
- Execução direta dos comandos sugeridos no ambiente da discente (não apenas leitura).
- Conferência dos campos retornados pela API do Ollama (`total_duration`, `load_duration`, `eval_count`, `eval_duration`) com a [documentação oficial da API do Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md).
- Conferência do model card oficial no Hugging Face para número de parâmetros e licença do modelo.
- Inspeção manual dos arquivos de log e CSV gerados pelos scripts antes de citá-los no relatório.
