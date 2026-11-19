"""Treina, avalia e exporta artefatos; usado também pelos notebooks entregues."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import pandas as pd
import joblib
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.metrics import silhouette_score, davies_bouldin_score
from . import VERSAO
from .dados import RAIZ, carregar_diario
from .features import COLUNAS_REGRESSAO, COLUNAS_GRUPO, tabela_regressao, tabela_grupos


def salvar_json(caminho, dados):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    Path(caminho).write_text(json.dumps(dados, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def metricas_regressao(y, previsto):
    return {"mae_kwh":float(mean_absolute_error(y, previsto)),
            "rmse_kwh":float(root_mean_squared_error(y, previsto)),
            "r2":float(r2_score(y, previsto))}


def treinar_regressao():
    tabela = tabela_regressao(carregar_diario())
    corte = int(len(tabela) * .8)
    desenvolvimento, teste = tabela.iloc[:corte], tabela.iloc[corte:]
    corte_interno = int(len(desenvolvimento) * .8)
    treino, validacao = desenvolvimento.iloc[:corte_interno], desenvolvimento.iloc[corte_interno:]
    candidatos = []
    # Ajuste pequeno, determinado antes de olhar o teste final.
    for profundidade, folha in [(4,5), (8,5), (None,5), (8,10)]:
        modelo = RandomForestRegressor(n_estimators=160, max_depth=profundidade,
                                      min_samples_leaf=folha, random_state=42, n_jobs=1)
        modelo.fit(treino[COLUNAS_REGRESSAO], treino.alvo_kwh)
        mae = mean_absolute_error(validacao.alvo_kwh, modelo.predict(validacao[COLUNAS_REGRESSAO]))
        candidatos.append({"max_depth":profundidade, "min_samples_leaf":folha, "mae_validacao_kwh":float(mae)})
    melhor = min(candidatos, key=lambda r:r["mae_validacao_kwh"])
    modelo = RandomForestRegressor(n_estimators=160, max_depth=melhor["max_depth"],
                                  min_samples_leaf=melhor["min_samples_leaf"], random_state=42, n_jobs=1)
    modelo.fit(desenvolvimento[COLUNAS_REGRESSAO], desenvolvimento.alvo_kwh)
    previsto = modelo.predict(teste[COLUNAS_REGRESSAO])
    referencias = {"ultimo_dia":teste.lag_1.to_numpy(),
                   "mesmo_dia_semana_anterior":teste.lag_7.to_numpy(),
                   "media_7_dias":teste[COLUNAS_REGRESSAO[:7]].mean(axis=1).to_numpy()}
    avaliacao = {"modelo":"RandomForestRegressor", "unidade":"kWh/dia", "versao":VERSAO,
                "amostras":len(tabela), "amostras_treino_final":len(desenvolvimento),
                "amostras_teste":len(teste), "selecao_hiperparametros":candidatos,
                "parametros_escolhidos":melhor,
                "periodo_treino":[str(desenvolvimento.data_alvo.min().date()),str(desenvolvimento.data_alvo.max().date())],
                "periodo_teste":[str(teste.data_alvo.min().date()),str(teste.data_alvo.max().date())],
                "teste_modelo":metricas_regressao(teste.alvo_kwh, previsto),
                "teste_baselines":{k:metricas_regressao(teste.alvo_kwh,v) for k,v in referencias.items()},
                "metodo":"Holdout cronológico 80/20. Hiperparâmetros selecionados em holdout interno 80/20 do desenvolvimento. Teste final nunca entra no fit.",
                "limite":"Teste em período posterior da mesma casa; não mede desempenho em outras casas ou no Brasil."}
    tabela["particao"] = ["treino" if i < corte else "teste" for i in range(len(tabela))]
    tabela.to_csv(RAIZ / "dados/treinamento_regressao.csv", index=False)
    resultado = teste[["data_alvo","alvo_kwh"]].copy()
    resultado["previsto_kwh"] = previsto
    for nome,v in referencias.items(): resultado[nome] = v
    (RAIZ / "resultados").mkdir(exist_ok=True)
    resultado.to_csv(RAIZ / "resultados/previsoes_teste.csv", index=False)
    salvar_json(RAIZ / "resultados/metricas_regressao.json", avaliacao)
    bundle = {"modelo":modelo, "colunas":COLUNAS_REGRESSAO, "versao":VERSAO,
              "sklearn":sklearn.__version__, "tipo":"regressao", "avaliacao":avaliacao,
              "faixa_diaria_treino":[float(desenvolvimento[COLUNAS_REGRESSAO[:7]].min().min()),
                                      float(desenvolvimento[COLUNAS_REGRESSAO[:7]].max().max())]}
    (RAIZ / "modelos").mkdir(exist_ok=True)
    joblib.dump(bundle, RAIZ / "modelos/previsao.joblib", compress=3)
    return avaliacao, resultado


def qualidade_grupos(x, grupos):
    n = len(set(grupos))
    if n < 2 or n >= len(x):
        return {"silhouette":None, "davies_bouldin":None,
                "observacao":"Métrica indefinida: menos de dois grupos ocupados ou grupo por amostra."}
    return {"silhouette":float(silhouette_score(x, grupos)),
            "davies_bouldin":float(davies_bouldin_score(x, grupos))}


def treinar_agrupamento():
    tabela = tabela_grupos(carregar_diario())
    corte = int(len(tabela) * .8)
    treino, teste = tabela.iloc[:corte], tabela.iloc[corte:]
    candidatos, pipelines = [], {}
    for k in range(2,6):
        pipe = Pipeline([("escala",StandardScaler()),
                         ("kmeans",KMeans(n_clusters=k, n_init=20, random_state=42))])
        pipe.fit(treino[COLUNAS_GRUPO])
        x = pipe.named_steps["escala"].transform(treino[COLUNAS_GRUPO])
        rotulos = pipe.named_steps["kmeans"].labels_
        candidatos.append({"k":k, **qualidade_grupos(x,rotulos)})
        pipelines[k] = pipe
    escolhido = max(candidatos, key=lambda r:r["silhouette"])["k"]
    pipe = pipelines[escolhido]
    rotulos = pipe.predict(treino[COLUNAS_GRUPO])
    resumo = treino[COLUNAS_GRUPO].copy()
    resumo["grupo"] = rotulos
    centros = resumo.groupby("grupo")[COLUNAS_GRUPO].mean()
    ordem = centros.media_kwh.sort_values().index.tolist()
    descricoes = {}
    for pos,grupo in enumerate(ordem):
        nome = "Menor" if pos == 0 else "Maior" if pos == len(ordem)-1 else "Intermediária"
        descricoes[str(grupo)] = {"nome":f"{nome} intensidade relativa ({pos+1}/{escolhido})",
                                  "media_diaria_treino_kwh":float(centros.loc[grupo,"media_kwh"]),
                                  "semanas_treino":int((rotulos == grupo).sum()),
                                  "interpretacao":"Comparação com semanas da casa de referência; não identifica desperdício nem causa."}
    teste_grupos = pipe.predict(teste[COLUNAS_GRUPO])
    xteste = pipe.named_steps["escala"].transform(teste[COLUNAS_GRUPO])
    avaliacao = {"modelo":"StandardScaler + KMeans", "versao":VERSAO, "k_escolhido":escolhido,
                "semanas_treino":len(treino), "semanas_teste":len(teste),
                "periodo_treino":[str(treino.data_inicio.min().date()), str(treino.data_fim.max().date())],
                "periodo_teste":[str(teste.data_inicio.min().date()), str(teste.data_fim.max().date())],
                "candidatos_treino":candidatos, "qualidade_teste":qualidade_grupos(xteste,teste_grupos),
                "grupos":descricoes,
                "metodo":"Semanas segunda-domingo sem sobreposição. Corte cronológico 80/20. Escala e KMeans ajustados só no treino; k por silhouette do treino, teste descritivo separado.",
                "limite":"Agrupamento exploratório sem rótulo verdadeiro; silhouette não é acurácia. Uma casa não representa a população."}
    tabela["particao"] = ["treino" if i < corte else "teste" for i in range(len(tabela))]
    tabela["grupo"] = pipe.predict(tabela[COLUNAS_GRUPO])
    tabela.to_csv(RAIZ / "dados/treinamento_agrupamento.csv", index=False)
    salvar_json(RAIZ / "resultados/metricas_agrupamento.json", avaliacao)
    centros.to_csv(RAIZ / "resultados/perfis_grupos_treino.csv")
    bundle = {"modelo":pipe, "colunas":COLUNAS_GRUPO, "versao":VERSAO,
              "sklearn":sklearn.__version__, "tipo":"agrupamento", "avaliacao":avaliacao,
              "descricoes":descricoes,
              "minimos_treino":treino[COLUNAS_GRUPO].min().to_dict(),
              "maximos_treino":treino[COLUNAS_GRUPO].max().to_dict()}
    joblib.dump(bundle, RAIZ / "modelos/agrupamento.joblib", compress=3)
    return avaliacao, tabela


def registrar_ambiente():
    import scipy, matplotlib
    from importlib.metadata import version
    pacotes = ["numpy","pandas","scipy","scikit-learn","joblib","matplotlib","Flask",
               "nbformat","nbclient","ipykernel","pytest"]
    versoes = {p:version(p) for p in pacotes}
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (RAIZ / "modelos").glob("*.joblib")}
    salvar_json(RAIZ / "modelos/manifesto.json", {"versao":VERSAO,"python":platform.python_version(),
                "pacotes":versoes,"sha256_modelos":hashes,"ambiente_testado":platform.system()})
    return versoes
