# Atribuição dos dados derivados

Fonte: Hebrail, G.; Berard, A. (2006). **Individual Household Electric Power Consumption**
[Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C58K54.

Licença da fonte: **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
Texto da licença: https://creativecommons.org/licenses/by/4.0/.
Página consultada em 11/11/2026:
https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption.

Mudanças feitas pelo projeto: seleção da potência ativa global, conversão de minuto para
energia diária, auditoria de cobertura, exclusão de dias incompletos e criação de atributos
de janelas diárias/semanais. Dados derivados estão nos CSVs de `dados/`.
O ZIP original de ~20 MB não é incluído; `preparar_dados.py` permite baixá-lo e reproduzir a transformação.
`dados/fonte.json` guarda o hash da fonte utilizada e as contagens.

A fonte não endossa o EcoLar e não representa consumidores brasileiros. Não foram
alteradas as datas para fazer os dados históricos parecerem medições atuais do grupo.
