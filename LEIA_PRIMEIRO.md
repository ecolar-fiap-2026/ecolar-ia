# EcoLar IA — abra esta pasta no VS Code

Projeto para **Artificial Intelligence & Chatbot — FIAP / GS 2026.2**.
Dois modelos realmente treinados (regressão e agrupamento), notebooks com saídas,
dados de treinamento, API Flask e testes. O banco e a entrega procedural de Python
recebidos do grupo não foram alterados.

## 1. Primeiro teste no Windows

1. Extraia o ZIP inteiro (não execute de dentro do ZIP).
2. No VS Code, escolha **Arquivo → Abrir Pasta** e selecione **EcoLar_IA**.
3. Use **Python 3.12 de 64 bits**. Confira no terminal: `py -3.12 --version`.
   Se essa versão não estiver instalada, instale-a em https://www.python.org/downloads/.
   O ambiente inicial foi Python 3.12.14/Linux. Yan validou também Python 3.12.10/Windows e VS Code em 11/11/2026; veja docs/VALIDACAO.md.
4. Execute **CONFIGURAR_WINDOWS.bat** e aguarde a instalação (internet necessária na primeira vez).
   Não é necessário abrir como administrador.
5. Execute **INICIAR_API_WINDOWS.bat**. Deixe a janela aberta.
6. No navegador, abra **http://127.0.0.1:5000**.
7. Clique em **Prever próximo dia** e **Analisar padrão**. As duas respostas devem ser HTTP 200.
8. Envie ao Chat os prints dos resultados ou qualquer erro. Encerre a API com Ctrl+C.

Os modelos estão prontos; **não é preciso treinar ou baixar dados para fazer este teste**.
A página mostra um exemplo real da base UCI, sem representar moradores do grupo.

### Alternativa pelo terminal PowerShell do VS Code

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Usar o executável diretamente dispensa ativar scripts do PowerShell.
No macOS/Linux: `python3.12 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`
e `.venv/bin/python app.py`.

## 2. Conferir a API e executar os testes

Com a API aberta, em **outro terminal**, execute:

```powershell
.\.venv\Scripts\python.exe testar_api.py
```

Esse cliente faz HTTP real para `/health`, `/prever` e `/agrupar`.
Para verificar dados, contrato, inferência e erros automaticamente:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Também existe **TESTAR_WINDOWS.bat**. A suíte usa o cliente de teste do Flask;
não precisa deixar o servidor aberto. Confira o resultado registrado em `docs/VALIDACAO.md`.

## 3. Abrir e executar os notebooks

Instale as extensões **Python** e **Jupyter**, da Microsoft, no VS Code.
Abra `notebooks/01_previsao.ipynb`, selecione o kernel **Python Environments → .venv**
e clique em **Run All / Executar Tudo**. Depois faça o mesmo no `02_agrupamento.ipynb`.
Os dois já contêm resultados reais da preparação; executá-los novamente refaz treinamento,
avaliação, CSVs e exportação. Feche e reabra a API depois de retreinar para carregar a nova versão.

Se não aparecer `.venv`, use Ctrl+Shift+P → **Python: Select Interpreter** →
selecione `.venv\Scripts\python.exe`; depois selecione esse ambiente no notebook.

Alternativa sem interface de notebook:

```powershell
.\.venv\Scripts\python.exe treinar.py
```

O treinamento usa os CSVs incluídos e não depende de Oracle ou internet.
Para refazer também a conversão da fonte original: `python preparar_dados.py` (download de ~20 MB).

## 4. O que foi implementado

| Pasta/arquivo | Conteúdo |
|---|---|
| `dados/` | Dias auditados, dias completos, tabelas exatas de treino/teste e origem |
| `notebooks/` | Análise exploratória, preparação, treinamento, métricas e gráficos |
| `modelos/` | Dois `.joblib` treinados e manifesto de versões/hashes |
| `ecolar_ia/` | Transformações, validação, preparo e treinamento reutilizáveis |
| `app.py` | API Flask que carrega e utiliza os modelos |
| `templates/` | Página local para testar os dois endpoints |
| `resultados/` | Métricas, previsões fora do treino, perfis e gráficos |
| `tests/` | Validação automática do projeto |
| `docs/` | API, integração Java/Oracle, resultados, roteiro e uso de IA |
| `IDENTIFICACAO_GRUPO.txt` | Identificação e explicações para a entrega |

Leia `docs/RESULTADOS.md` antes de explicar o desempenho: a média de sete dias tem
MAE ligeiramente menor que Random Forest no teste, e o agrupamento é exploratório.
Não apresentamos uma taxa de "acerto" inventada.

## 5. Integração e limites

Este módulo **não se conecta automaticamente ao Oracle nem ao JSON do Python**.
O contrato está pronto para Java: consultar sete dias consecutivos no Oracle, chamar o Flask
e persistir o resultado com `origem=MODELO`. Veja `docs/INTEGRACAO_JAVA_ORACLE.md`.
Sem código Java fornecido nesta etapa, essa integração completa ainda não foi executada.

O treinamento usa uma casa francesa de 2006–2010; não é um modelo validado em casas brasileiras.
Os 60 registros simulados do banco não foram usados como evidência de treinamento.
Não existe promessa de economia ou estimativa completa da fatura.

O servidor de demonstração roda somente no computador local (127.0.0.1), sem autenticação;
não é uma implantação pública. A API deve receber chamadas do Java, não credenciais Oracle pelo navegador.
Os `.joblib` são arquivos Python serializados: carregue apenas os produzidos por este projeto ou por você.

## 6. Problemas comuns

| Mensagem/situação | Ação |
|---|---|
| `No suitable Python runtime found` | Instale Python 3.12 de 64 bits; confira `py -0p` |
| `ModuleNotFoundError` | Use `.venv\Scripts\python.exe` e instale `requirements.txt` |
| Página não abre | Deixe `app.py` aberto e confira a URL e mensagens do terminal |
| Porta 5000 ocupada | Encerre a outra execução da API; não abra dois servidores |
| HTTP 503 | Confira arquivos em `modelos/` e versão instalada de scikit-learn; retreine com `treinar.py` se necessário |
| HTTP 400 | Confira sete registros, datas consecutivas, ordem e números não negativos |
| Instalação de SciPy/NumPy tenta compilar | Confira Python 3.12 de 64 bits e conexão com o PyPI |
| Kernel errado | Selecione `.venv`, não o Python de outro projeto |

## 7. Antes de enviar no Portal

O pacote cobre os arquivos exigidos nas páginas 23–28 do enunciado: dados, notebooks,
modelos, Flask e TXT. Yan executou os dois notebooks, a API e os 42 testes em seu Windows. O grupo deve revisar os resultados, confirmar a identificação oficial, compreender o código e repetir a demonstração se usar outro equipamento.
Entrega prevista: 19/11/2026 às 23h55. Apresentação presencial: 23 a 27/11, conforme a disciplina.
Não inclua `.venv`, caches ou credenciais no ZIP. As saídas dos notebooks devem permanecer.

## Fontes

- Enunciado FIAP fornecido pelo grupo, Artificial Intelligence & Chatbot, pp. 23–28.
- Hebrail, G.; Berard, A. Individual Household Electric Power Consumption. UCI.
  https://doi.org/10.24432/C58K54 — CC BY 4.0. Consulta 11/11/2026.
- scikit-learn: https://scikit-learn.org/stable/ ; persistência: https://scikit-learn.org/stable/model_persistence.html
- Flask: https://flask.palletsprojects.com/en/stable/testing/
- Requisitos de domínio: PDFs de Business Model e banco, e ZIP Python recebidos em 11/11/2026.
