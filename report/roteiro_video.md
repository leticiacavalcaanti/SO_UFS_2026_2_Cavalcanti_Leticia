# Roteiro do vídeo (alvo: 9 min — máximo 10 min)

Grave com câmera/rosto visível na abertura (identificação) e tela compartilhada no restante.
Use `report/apresentacao.pdf` como apoio visual (pode deixar aberto e ir passando os slides).

As falas abaixo são um guia pra você falar com suas palavras — não precisa decorar nem ler
palavra por palavra. Leia uma vez antes de gravar, entenda a ideia de cada bloco, e fale
naturalmente. Está escrito em tom de fala (com "deixa eu", "né", contrações) de propósito,
pra não soar como leitura.

---

## 0:00–0:45 — Identificação e trilha
**AÇÃO:** câmera ligada, rosto visível. Pode deixar o slide 1 (título) aberto atrás ou em tela cheia da câmera.

**FALA:**
"Oi! Meu nome é Letícia Cavalcanti, e esse é o vídeo da Atividade 1 de Sistemas Operacionais.
Eu escolhi a Trilha A, que é o chat local usando Ollama junto com o Open WebUI, e o modelo que
eu rodei foi o Llama 3.2, na versão de 3 bilhões de parâmetros, com quantização Q4_K_M. Ao longo
do vídeo eu vou mostrar como montei o ambiente, o que eu observei nos processos e threads, e os
resultados dos experimentos que fiz comparando diferentes configurações."

---

## 0:45–2:00 — Ambiente e arquitetura
**AÇÃO:**
- Mostrar terminal com `docker compose ps` rodando (containers `ollama` e `open-webui` saudáveis).
- Mostrar rapidamente `data/ambiente_inventario.txt` (destacar CPU, RAM, ausência de GPU).
- Deixar o slide 2/3 (arquitetura) em tela enquanto fala a última parte.

**FALA:**
"Antes de entrar na demonstração, deixa eu explicar rapidinho o ambiente que eu usei. Como eu
tô no Windows, eu rodei tudo dentro de containers Docker, usando o Docker Desktop com o WSL2 por
baixo — então o ambiente Linux que a atividade pede vem daí, de dentro desses containers. Esse
notebook não tem GPU dedicada, então toda a inferência roda direto na CPU: um Intel i5 de décima
geração, com 4 núcleos liberados pro Docker e pouco menos de 6 gigas de RAM.

A arquitetura é simples: eu acesso o Open WebUI pelo navegador, na porta 3000; ele conversa com
o Ollama através de uma API HTTP local, na porta 11434; e é o Ollama quem carrega o modelo e faz
a inferência de fato."

---

## 2:00–3:30 — Demonstração ao vivo
**AÇÃO:**
- Abrir http://localhost:3000, **criar um chat novo** (não usar um chat antigo com histórico).
- Digitar o prompt curto: *"Explique em uma frase o que é um processo em sistemas operacionais."*
- Enquanto a resposta carrega, abrir um terminal e rodar:
  `docker exec ollama ps -eo pid,ppid,nlwp,pcpu,comm --sort=-pcpu`

**FALA:**
"Agora deixa eu mostrar funcionando de verdade. Vou abrir o Open WebUI aqui, começar uma
conversa nova, e mandar uma pergunta simples pro modelo, só pra gente ver a responsividade numa
situação padrão.

Enquanto ele processa, eu vou abrir um terminal do lado e mostrar o processo rodando dentro do
container... reparem que aparece esse processo aqui, o `llama-server` — é ele quem é criado na
hora pra atender essa requisição."

---

## 3:30–5:00 — Processos, threads e chamadas de sistema
**AÇÃO:**
- Mostrar `data/ps_snapshots/03_durante_inferencia_ps.txt` e `04_durante_inferencia_threads.txt`.
- Mostrar `data/strace/strace-resumo.txt`, destacando a linha do `futex`.

**FALA:**
"Sobre os processos: quando o container tá parado, só o `ollama serve` roda, com PID 1 e cerca
de 25 threads — ele funciona como um supervisor, esperando requisições. Só quando chega uma
pergunta de verdade é que ele cria um processo filho, o `llama-server`, que é quem faz o trabalho
pesado de carregar os pesos e gerar a resposta.

Eu também rodei um `strace` numa requisição controlada pra ver quais chamadas de sistema mais
apareciam. A chamada `futex` sozinha correspondeu a quase 73% do tempo total — faz todo sentido,
porque é ela que sincroniza as threads que estão processando a inferência em paralelo. Também
apareceu bastante `read` e `openat`, ligados à leitura dos pesos do modelo, e `epoll_pwait` e
`socket`, do servidor HTTP local."

---

## 5:00–7:30 — Resultados dos experimentos
**AÇÃO:** mostrar `data/experimentos/tabelas_resumo.md` e os gráficos
(`grafico_concorrencia.png`, `grafico_contexto.png`) — ou os slides 7 e 8.

**FALA:**
"Agora, a parte que eu achei mais interessante: os experimentos comparativos. No total eu rodei
12 execuções, cobrindo três configurações diferentes.

Na primeira, eu comparei um prompt curto com um prompt longo, do jeito padrão — o prompt longo
demorou bem mais, como já era esperado.

Mas na segunda configuração eu testei concorrência: mandei quatro requisições ao mesmo tempo, em
vez de uma de cada vez. E o resultado foi bem revelador — em vez de melhorar a vazão, isso
piorou tudo. A CPU do container ficou saturada, entre 55 e 75% de uso, e 75% dessas requisições
simplesmente deram timeout, sem completar nem em 5 minutos. Ou seja, esse notebook não tem
núcleo de sobra pra atender vários pedidos ao mesmo tempo nesse modelo.

Na terceira configuração eu mexi no tamanho do contexto, comparando 2048 com 8192 tokens.
Aumentar o contexto trouxe 21% a mais de tempo de resposta e 30% a mais de uso de memória — e
toda vez que eu trocava esse parâmetro, o Ollama precisava recarregar o modelo do zero, o que
adicionava mais alguns segundos."

---

## 7:30–8:30 — Limites, riscos e decisões
**AÇÃO:** slide 9/10 em tela.

**FALA:**
"Vale registrar algumas limitações desse experimento. Primeiro, eu não tive como comparar CPU
com GPU, porque esse notebook não tem GPU dedicada — tudo rodou só em CPU. Segundo, como eu tô
usando Docker Desktop com WSL2, existe uma camada extra de virtualização que pode ter introduzido
algum ruído nos tempos que eu medi. E terceiro, minha amostra é pequena, só 12 execuções, então
esses números servem mais como indício do que como uma medição super robusta.

Também tomei uma decisão importante: o repositório oficial do Llama 3.2 3B no Hugging Face é
fechado, então usei a versão GGUF que já vem pronta na biblioteca do próprio Ollama — é o mesmo
modelo-base, só que sem precisar de autenticação."

---

## 8:30–9:00 — Conclusão
**AÇÃO:** voltar câmera pro rosto, ou deixar o slide final com o link do repositório.

**FALA:**
"Fechando: o que eu percebi com esse experimento é que a responsividade de um sistema local de
IA generativa depende menos do tamanho do modelo — que aqui era fixo, 3 bilhões de parâmetros —
e muito mais de como você configura a execução: quantas requisições simultâneas, qual o tamanho
do contexto. Essas escolhas interagem diretamente com o escalonamento e os limites de hardware
do sistema operacional por baixo.

Todo o código, os scripts, os dados e o relatório completo estão no repositório do GitHub, o
link tá na descrição. Obrigada!"

---
### Checklist antes de gravar
- [ ] `docker compose up -d` rodando (containers saudáveis)
- [ ] Terminal com `data/` acessível para mostrar os arquivos
- [ ] `report/apresentacao.pdf` aberto como apoio visual
- [ ] Chat novo criado no Open WebUI (sem histórico acumulado)
- [ ] Cronômetro visível para não passar de 10 minutos
