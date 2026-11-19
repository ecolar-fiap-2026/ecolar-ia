# Resultados reais da preparação — 11/11/2026

Experimentos executados com os CSVs incluídos e algoritmos exportados; não são valores de exemplo fixados no código.

## Dados

Fonte UCI: 2,075,259 leituras por minuto; 1442 dias; 1358 completos aceitos e 84 excluídos. Nenhuma ausência preenchida com zero.

Regressão: 909 janelas, 727 de desenvolvimento e 182 de teste. Hiperparâmetros selecionados em validação interna cronológica.
Teste de 2010-03-08 a 2010-11-25. Treino termina em 2010-03-07.

## Regressão: quanto menor MAE/RMSE, melhor

| Método | MAE (kWh) | RMSE (kWh) | R² |
|---|---:|---:|---:|
| Random Forest | 3.8938 | 5.2939 | 0.4844 |
| ultimo_dia | 4.5524 | 6.4734 | 0.2290 |
| mesmo_dia_semana_anterior | 5.4883 | 7.4142 | -0.0114 |
| media_7_dias | 3.8808 | 5.4575 | 0.4520 |

A média dos sete dias tem MAE ligeiramente menor que Random Forest. O modelo reduz RMSE frente às três referências. Essa comparação não prova superioridade geral. Não reajustamos usando o teste final.

MAE/RMSE são erros em kWh/dia; não confundir com percentual de acerto, intervalo de confiança ou economia obtida.

## Agrupamento

110 semanas de treino e 28 de teste. Escolha de k entre 2 e 5 pela silhouette de treino. Resultado escolhido: **k=2**.

| Partição | Silhouette | Davies–Bouldin |
|---|---:|---:|
| Treino | 0.4302 | 0.8355 |
| Teste posterior | 0.2438 | 1.0212 |

Silhouette maior indica melhor separação relativa; Davies–Bouldin menor é melhor. A separação cai no teste, reforçando que os grupos são exploratórios. Não há acurácia supervisionada.

| Grupo | Interpretação relativa | Média diária das semanas de treino |
|---|---|---:|
| 0 | Menor intensidade relativa (1/2) | 19.347 kWh |
| 1 | Maior intensidade relativa (2/2) | 32.099 kWh |

Os grupos não indicam desperdício nem causa. Referem-se às semanas da casa da fonte, não a tipos comprovados de família.

## Limitações e evolução

- Uma casa estrangeira e histórica; sem generalização demonstrada para o Brasil.
- Excluir dias incompletos pode mudar a distribuição; o filtro e a cobertura estão auditados.
- Teste temporal é um passo à frente com observações anteriores disponíveis; não é previsão recursiva de meses.
- Os atributos de agrupamento priorizam intensidade e são correlacionados.
- Não há clima, ocupação ou intervenções para comprovar economia causal.
- Próximo passo: dados locais, múltiplas casas, validação temporal adicional e estudo com usuários.

Arquivos detalhados: metricas_regressao.json, metricas_agrupamento.json, previsoes_teste.csv e perfis_grupos_treino.csv, na pasta resultados/.
