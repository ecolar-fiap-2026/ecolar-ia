# Demonstração e estudo — sugestão de 6 minutos

O tempo abaixo é sugestão de ensaio, não tempo imposto pelo enunciado de IA.
Todos os integrantes precisam compreender o projeto e responder perguntas.

1. **Problema (40 s):** o morador precisa acompanhar consumo; a IA estima um próximo dia
   e compara características de semanas. Não é detector comprovado de desperdício.
2. **Dados (60 s):** mostrar fonte UCI, regra kW/60 por minuto, exclusão de dias incompletos
   e limitação de uma residência francesa. Distinguir de dados sintéticos do Oracle.
3. **Regressão (80 s):** mostrar sete dias de entrada, corte cronológico, MAE/RMSE e baselines.
   Explicar que a média móvel tem MAE ligeiramente menor, enquanto o modelo melhora RMSE.
4. **Agrupamento (60 s):** mostrar padronização só no treino, escolha de k e interpretação
   relativa dos grupos. Silhouette não é percentual de acerto.
5. **API (80 s):** abrir a página local; clicar nas duas análises; mostrar resposta. Remover um
   dia e comprovar HTTP 400. Abrir um `.joblib` só pelo código, nunca como texto no editor.
6. **Integração e limites (40 s):** Java será responsável por Oracle e por chamar o Flask;
   demonstrar apenas o que estiver implementado no momento. Informar ausência de validação brasileira.

## Perguntas que o grupo deve saber responder

- Por que dividimos potência por 60? Porque kW × 1/60 de hora = kWh por minuto.
- Por que precisamos de oito dias na amostra de treinamento? Sete de entrada e um alvo real.
- Por que não embaralhar? Queremos avaliar uma previsão em período posterior ao treinamento.
- O que significa MAE 3,89? Erro absoluto médio de aproximadamente 3,89 kWh/dia nesse teste,
  não porcentagem de acerto nem garantia para uma nova residência.
- A IA sempre vence regra simples? Não. O baseline de média móvel merece ser comparado.
- O que foi salvo? Regressor treinado e pipeline completo da escala + KMeans, com metadados.
- A API treina toda vez? Não. Carrega os modelos e chama `predict`.
- Grupo 1 significa desperdício? Não; é um identificador arbitrário de intensidade relativa.
- Existe ligação automática com o Python JSON? Não. É um módulo independente com contrato HTTP.
- Precisa de Oracle para testar agora? Não. Somente para a integração completa posterior do Java.

Antes da apresentação, fazer o teste no equipamento real e manter a pasta completa disponível.
