# Validação do pacote de IA — 11/11/2026

## Execução feita por Yan no Windows

Ambiente: Python 3.12.10, .venv, VS Code/Jupyter e navegador local. O manifesto
modelos/manifesto.json registra Windows e as versões utilizadas. O ZIP enviado
contém os notebooks executados e os dois modelos exportados nesse ambiente.

| Verificação | Evidência observada |
|---|---|
| Instalação | Ambiente concluído e Flask iniciado em 127.0.0.1:5000 |
| Testes | Captura do terminal: 42 passed in 5.70s |
| Notebook 01 | Células 1–7 executadas, sem saídas de erro; exportação de previsao.joblib |
| Notebook 02 | Células 1–6 executadas, sem saídas de erro; exportação de agrupamento.joblib |
| Previsão após reiniciar | HTTP 200; 28,01 kWh para 08/03/2010, com o histórico do exemplo |
| Agrupamento após reiniciar | HTTP 200; grupo 0; menor intensidade relativa; média 16,632 kWh/dia |
| Entrada inválida | Histórico vazio rejeitado com HTTP 400 e explicação sobre sete dias |

Capturas fornecidas por Yan em evidencias_windows/, apenas enquadradas para mostrar
os resultados. Não foram alterados valores, respostas ou mensagens.

## Revisão do ZIP recebido

- Arquivo íntegro, sem .venv, __pycache__ ou .pytest_cache.
- Dados de treinamento, dois .ipynb, dois .joblib, código Flask e TXT presentes.
- Todas as células de código têm execução registrada e não contêm saídas de erro.
- Hashes dos modelos conferem com o manifesto gerado no Windows.
- Código Python recebido idêntico ao projeto preparado. Nenhum modelo retreinado
  nesta revisão: foram preservados os arquivos exportados por Yan.
- Alterações desta revisão: documentação atualizada, registro de validação e capturas.

## Preparação e testes locais anteriores

Ambiente inicial: Linux / Python 3.12.14. Fonte oficial UCI: 2.075.259 linhas,
1.358 dias completos e 84 excluídos. Origem/hash em dados/fonte.json.
Treinamento, avaliação temporal, exportação e inspeção dos gráficos executados.
Os notebooks inicialmente foram executados por IPython local; Yan posteriormente
executou-os com Jupyter no VS Code/Windows, conforme evidências acima.

A suíte de 42 testes confere contrato, inferência real, entradas inválidas, falha de
modelos, avisos, todas as lags e padronização ajustada apenas no treino.
Log inicial em RESULTADO_TESTES.txt; revisão dos artefatos recebidos em RESULTADO_REVISAO.txt.

HTTP real por TCP loopback também foi executado na preparação (Werkzeug + urllib):
página, health, previsão e agrupamento HTTP 200; histórico vazio HTTP 400.
O registro original está em resultados/teste_http.json; reproduzir com python verificar_http.py.

## Limites e próximos passos

- Operação local da IA validada; isso não comprova integração completa Java/Oracle.
- Implementar/testar Java → Flask e persistência Oracle conforme INTEGRACAO_JAVA_ORACLE.md.
- Confirmar identificação oficial, revisar o conteúdo e estudar os resultados. A execução
  de Yan não comprova domínio técnico ou revisão completa de todos os integrantes.
- Repetir a demonstração se o computador da apresentação for outro.
- Servidor Flask local de demonstração não é implantação pública de produção.
