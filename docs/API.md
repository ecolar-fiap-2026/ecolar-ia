# Contrato da API — ecolar-ia-1.0

Base local: `http://127.0.0.1:5000`. Início: `python app.py`.
JSON em UTF-8; cabeçalho `Content-Type: application/json`. Servidor local sem CORS
porque a página de teste tem a mesma origem e a integração planejada é Java → Flask.

| Método/rota | Resultado |
|---|---|
| GET `/` | Página de teste dos dois modelos |
| GET `/health` | 200 com modelos carregados ou 503 se indisponíveis |
| POST `/prever` | Previsão do dia seguinte ao último dia informado |
| POST `/agrupar` | Grupo de padrão da janela e interpretação relativa |

## Entrada comum dos dois POSTs

`exemplos/requisicao.json` contém um exemplo real de sete dias da fonte UCI,
na partição de teste. Campo raiz único: `historico`.

Cada registro tem somente `data` (ISO AAAA-MM-DD) e `consumo_kwh` (número JSON).
Exatamente sete dias, em ordem crescente, consecutivos e sem duplicatas. Datas não podem
estar no futuro do servidor; intervalo suportado 1900–2200. Consumos devem ser finitos,
não negativos e no máximo 10000 kWh/dia (limite técnico de entrada, não limite de normalidade).
Booleanos, strings numéricas, campos extras, nulos e JSON inválido são rejeitados.
O corpo é limitado a 16 KiB. Não envie leitura acumulada, potência em W ou conta mensal.

## Saída da previsão

- `data_referencia`: último dia observado.
- `data_alvo`: referência + um dia.
- `consumo_previsto_kwh`: previsão numérica, arredondada para três casas.
- `modelo`: identificação/versionamento do algoritmo.
- `origem`: `MODELO`, pois há inferência real por um estimador treinado.
- `avisos`: limitações de domínio; alerta adicional se consumos saírem da faixa do treino.

Não há intervalo de confiança calculado. Erro médio não é probabilidade de acerto.
A referência pode ser histórica para reprodução dos experimentos.

## Saída do agrupamento

- `data_inicio` e `data_fim`: intervalo de sete dias.
- `grupo`: inteiro identificador arbitrário do cluster.
- `nome`: intensidade relativa com base na média das semanas de treino.
- `interpretacao`: significado e limite do agrupamento.
- `media_janela_kwh`: média dos sete dias informados.
- `modelo`, `origem` e `avisos`: rastreabilidade e limites.

Semanas de treino vão de segunda a domingo; janelas em outro alinhamento são aceitas com aviso.
Não significa desperdício, classe social, número de moradores ou causa do consumo.

## Erros

400: JSON/contrato/valores inválidos. 413: corpo acima do limite. 415: formato não JSON.
404: rota ausente. 405: método não permitido. 503: modelos ausentes, alterados ou incompatíveis.
Erro retorna JSON com `erro` e `mensagem`.

Modelos são carregados na inicialização e nunca retreinados por uma requisição.
Depois de retreinar, reinicie a API. `testar_api.py` permite testar por HTTP em outro terminal;
os testes automatizados também conferem igualdade entre inferência direta e resposta Flask.
