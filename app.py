"""API Flask: carrega os dois modelos treinados, sem treinar durante a requisição."""
from datetime import timedelta
from pathlib import Path
import hashlib
import json
import logging
import joblib
import pandas as pd
import sklearn
from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException
from ecolar_ia import VERSAO
from ecolar_ia.dados import RAIZ
from ecolar_ia.features import (validar_historico, EntradaInvalida, atributos_regressao,
                               atributos_grupo, COLUNAS_REGRESSAO, COLUNAS_GRUPO)

LIMITACAO = "Modelo demonstrativo treinado em uma casa francesa (2006-2010), sem validação em residências brasileiras. Não garante economia."


def carregar_modelos(pasta):
    """Falha explícita para arquivo ausente, alterado ou versão incompatível."""
    manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    if manifesto["pacotes"]["scikit-learn"] != sklearn.__version__:
        raise ValueError("Instale requirements.txt ou retreine com a versão instalada.")
    bundles = {}
    for nome, tipo, colunas in [("previsao", "regressao", COLUNAS_REGRESSAO),
                                ("agrupamento", "agrupamento", COLUNAS_GRUPO)]:
        caminho = pasta / f"{nome}.joblib"
        if hashlib.sha256(caminho.read_bytes()).hexdigest() != manifesto["sha256_modelos"][caminho.name]:
            raise ValueError("Modelo alterado: retreine e gere o manifesto novamente.")
        b = joblib.load(caminho)
        if b["tipo"] != tipo or b["colunas"] != colunas or b["versao"] != VERSAO:
            raise ValueError("Artefato incompatível com o contrato da API.")
        bundles[nome] = b
    return bundles


def create_app(pasta_modelos=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    try:
        bundles = carregar_modelos(Path(pasta_modelos) if pasta_modelos else RAIZ / "modelos")
        erro_modelos = None
    except Exception as erro:
        app.logger.error("Não foi possível carregar modelos: %s", erro)
        bundles, erro_modelos = {}, "Modelos indisponíveis. Confira requirements.txt, arquivos ou execute treinar.py."
    app.config["BUNDLES"] = bundles

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        return jsonify(erro=erro.name, mensagem=erro.description), erro.code

    @app.errorhandler(EntradaInvalida)
    def erro_entrada(erro):
        return jsonify(erro="entrada_invalida", mensagem=str(erro)), 400

    @app.get("/")
    def inicio():
        exemplo = json.loads((RAIZ / "exemplos/requisicao.json").read_text(encoding="utf-8"))
        return render_template("index.html", exemplo=exemplo)

    @app.get("/health")
    def health():
        return jsonify(status="ok" if bundles else "indisponivel", versao=VERSAO,
                       modelos=list(bundles), mensagem=erro_modelos), 200 if bundles else 503

    def entrada():
        if not request.is_json:
            return None, (jsonify(erro="tipo_invalido", mensagem="Use Content-Type: application/json."), 415)
        datas, valores = validar_historico(request.get_json())
        return (datas, valores), None

    @app.post("/prever")
    def prever():
        if not bundles:
            return jsonify(erro="modelos_indisponiveis", mensagem=erro_modelos), 503
        dados, erro = entrada()
        if erro: return erro
        datas, valores = dados
        alvo = datas[-1] + timedelta(days=1)
        b = bundles["previsao"]
        x = pd.DataFrame([atributos_regressao(valores, alvo)], columns=b["colunas"])
        previsto = float(b["modelo"].predict(x)[0])
        minimo, maximo = b["faixa_diaria_treino"]
        avisos = [LIMITACAO]
        if min(valores) < minimo or max(valores) > maximo:
            avisos.append("Há consumos fora da faixa diária observada no treino; resultado pode extrapolar o domínio validado.")
        return jsonify(data_referencia=datas[-1].isoformat(), data_alvo=alvo.isoformat(),
                       consumo_previsto_kwh=round(previsto,3), modelo=VERSAO + "/random-forest",
                       origem="MODELO", avisos=avisos)

    @app.post("/agrupar")
    def agrupar():
        if not bundles:
            return jsonify(erro="modelos_indisponiveis", mensagem=erro_modelos), 503
        dados, erro = entrada()
        if erro: return erro
        datas, valores = dados
        b = bundles["agrupamento"]
        x = pd.DataFrame([atributos_grupo(valores,datas)], columns=b["colunas"])
        grupo = int(b["modelo"].predict(x)[0])
        descricao = b["descricoes"][str(grupo)]
        avisos = [LIMITACAO]
        if datas[0].weekday() != 0:
            avisos.append("Janela fora do alinhamento segunda-domingo usado no treino; comparação exploratória.")
        if any(float(x[c].iloc[0]) < b["minimos_treino"][c] or
               float(x[c].iloc[0]) > b["maximos_treino"][c] for c in b["colunas"]):
            avisos.append("Há atributos fora da faixa do treino; o grupo é apenas o centroide mais próximo.")
        return jsonify(data_inicio=datas[0].isoformat(), data_fim=datas[-1].isoformat(),
                       grupo=grupo, nome=descricao["nome"], interpretacao=descricao["interpretacao"],
                       media_janela_kwh=round(sum(valores)/7,3),
                       modelo=VERSAO + "/kmeans", origem="MODELO", avisos=avisos)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
