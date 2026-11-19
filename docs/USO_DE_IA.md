# Uso de IA e revisão humana

Preparação em 11/11/2026 com ChatGPT/Codex: análise dos documentos recebidos,
seleção da abordagem, geração de código/notebooks/documentação e testes locais.
Yan relatou a execução no Windows por capturas, e os notebooks/modelos salvos foram conferidos no ZIP enviado. Isso comprova a execução, não permite presumir domínio técnico ou revisão completa de todos os integrantes.

Pedido do usuário: "quero que vc ja faça o arquivo so para eu importar no vscode e testar tudo com vc. Igual foi o de Banco!"

Decisões verificadas durante a implementação:

- A entrega Python usa JSON local; foi mantida, sem afirmar sincronização com Oracle.
- Os 30 consumos do banco e resultados fixtures são simulados. Não foram usados para sustentar treinamento.
- Fonte oficial UCI baixada; energia por minuto convertida para kWh e dias incompletos excluídos.
- Separação cronológica e padronização ajustada apenas no treino, para evitar vazamento.
- A regressão não venceu a média móvel em MAE. A comparação foi mantida, sem escolher
  novos parâmetros olhando o teste para fabricar melhora.
- O número de grupos foi escolhido por dados; não foi imposto para reproduzir fixtures do banco.
- Testes executam os estimadores exportados e verificam API, entradas inválidas e cortes temporais.
- A validação concluída por Yan no Windows e as limitações restantes são descritas em VALIDACAO.md.

## Execução e revisão pelos integrantes

1. Yan concluiu configuração, API e 42 testes no Windows; repetir se o equipamento da apresentação for outro.
2. Yan executou e salvou os dois notebooks com `.venv` no VS Code. Todos precisam explicar a conversão de unidades.
3. Entender treino/teste, MAE, RMSE, baselines, KMeans e limitações da silhouette.
4. Revisar os arquivos e anotar correções/decisões realmente feitas pelo grupo.
5. Cada integrante registrar em suas próprias palavras o que aprendeu e consegue demonstrar.

Este registro cobre a preparação por IA. A execução humana de Yan está documentada; isso não equivale à revisão completa e ao entendimento de todos. Acrescentar apenas decisões e aprendizados realmente relatados pelo grupo.
