### Tabela 1 - Resumo por configuracao/cenario (media por requisicao)

| Configuracao | Cenario | N | Tempo total medio (s) | TTFT medio (s) | Tokens/s medio | Erros |
|---|---|---|---|---|---|---|
| config1_padrao | padrao_curto | 2 | 9.802 | 0.569 | 6.57 | 0 |
| config1_padrao | padrao_longo | 2 | 188.749 | 2.33 | 5.17 | 0 |
| config2_concorrencia | concorrencia_1 | 2 | 166.877 | 0.143 | 5.13 | 0 |
| config2_concorrencia | concorrencia_4 | 8 | 191.551 | 0.152 | 4.98 | 6 |
| config3_contexto | num_ctx_2048 | 2 | 192.204 | 5.885 | 5.04 | 0 |
| config3_contexto | num_ctx_8192 | 2 | 232.857 | 6.387 | 4.14 | 0 |

### Tabela 2 - Uso de recursos por round

| Configuracao | Cenario | Round | Concorrencia | Wall time (s) | CPU (container) | Memoria (container) | Threads |
|---|---|---|---|---|---|---|---|
| config1_padrao | padrao_curto | 1 | 1 | 10.472 | 0.29% | 3.006GiB / 5.788GiB | 24 |
| config1_padrao | padrao_curto | 2 | 1 | 9.213 | 0.57% | 3.012GiB / 5.788GiB | 24 |
| config1_padrao | padrao_longo | 3 | 1 | 196.506 | 0.98% | 3.008GiB / 5.788GiB | 24 |
| config1_padrao | padrao_longo | 4 | 1 | 180.992 | 0.50% | 3.067GiB / 5.788GiB | 24 |
| config2_concorrencia | concorrencia_1 | 5 | 1 | 206.648 | 0.12% | 3.132GiB / 5.788GiB | 24 |
| config2_concorrencia | concorrencia_1 | 6 | 1 | 127.107 | 0.45% | 3.24GiB / 5.788GiB | 24 |
| config2_concorrencia | concorrencia_4 | 7 | 4 | 300.031 | 55.15% | 3.383GiB / 5.788GiB | 24 |
| config2_concorrencia | concorrencia_4 | 8 | 4 | 300.017 | 74.76% | 3.519GiB / 5.788GiB | 24 |
| config3_contexto | num_ctx_2048 | 9 | 1 | 188.405 | 0.40% | 2.747GiB / 5.788GiB | 24 |
| config3_contexto | num_ctx_2048 | 10 | 1 | 196.002 | 0.00% | 2.823GiB / 5.788GiB | 24 |
| config3_contexto | num_ctx_8192 | 11 | 1 | 249.409 | 0.76% | 3.58GiB / 5.788GiB | 24 |
| config3_contexto | num_ctx_8192 | 12 | 1 | 216.322 | 0.46% | 3.676GiB / 5.788GiB | 24 |
