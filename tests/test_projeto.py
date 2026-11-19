"""Testes do contrato HTTP, consistência de inferência e ausência de vazamento."""
from copy import deepcopy
from datetime import date, timedelta
import json
import math
import numpy as np
import pandas as pd
import pytest
from app import create_app, carregar_modelos
from ecolar_ia.dados import RAIZ, carregar_diario
from ecolar_ia.features import (atributos_regressao, atributos_grupo, validar_historico,
                               COLUNAS_REGRESSAO, COLUNAS_GRUPO)


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture()
def corpo():
    return json.loads((RAIZ / "exemplos/requisicao.json").read_text())


def test_health_e_pagina(client):
    assert client.get("/health").status_code == 200
    assert len(client.get("/health").json["modelos"]) == 2
    assert client.get("/").status_code == 200


@pytest.mark.parametrize("rota",["prever","agrupar"])
def test_modelo_real_serializado(client,corpo,rota):
    r = client.post("/"+rota,json=corpo)
    assert r.status_code == 200
    datas,valores = validar_historico(corpo)
    bundles = carregar_modelos(RAIZ / "modelos")
    if rota == "prever":
        x = pd.DataFrame([atributos_regressao(valores,datas[-1]+timedelta(days=1))],columns=COLUNAS_REGRESSAO)
        esperado = float(bundles["previsao"]["modelo"].predict(x)[0])
        assert r.json["consumo_previsto_kwh"] == round(esperado,3)
        assert r.json["data_alvo"] == "2010-03-08"
    else:
        x = pd.DataFrame([atributos_grupo(valores,datas)],columns=COLUNAS_GRUPO)
        assert r.json["grupo"] == int(bundles["agrupamento"]["modelo"].predict(x)[0])
    assert r.json["origem"] == "MODELO"
    assert r.json["avisos"]


@pytest.mark.parametrize("rota",["prever","agrupar"])
@pytest.mark.parametrize("erro",["curto","longo","lacuna","duplicata","invertido","negativo","texto",
                                 "booleano","nulo","nan","infinito","gigante","data","vazio","campo_extra"])
def test_entradas_invalidas(client,corpo,rota,erro):
    h = corpo["historico"]
    if erro == "curto": h.pop()
    elif erro == "longo": h.append(deepcopy(h[-1]))
    elif erro == "lacuna": h[-1]["data"] = "2010-03-09"
    elif erro == "duplicata": h[-1]["data"] = h[-2]["data"]
    elif erro == "invertido": h.reverse()
    elif erro == "negativo": h[0]["consumo_kwh"] = -1
    elif erro == "texto": h[0]["consumo_kwh"] = "10"
    elif erro == "booleano": h[0]["consumo_kwh"] = True
    elif erro == "nulo": h[0]["consumo_kwh"] = None
    elif erro == "nan": h[0]["consumo_kwh"] = float("nan")
    elif erro == "infinito": h[0]["consumo_kwh"] = float("inf")
    elif erro == "gigante": h[0]["consumo_kwh"] = 10001
    elif erro == "data": h[0]["data"] = "2010-02-30"
    elif erro == "vazio": corpo = {}
    elif erro == "campo_extra": corpo["cd_residencia"] = 1
    assert client.post("/"+rota,json=corpo).status_code == 400


def test_json_invalido_e_content_type(client):
    assert client.post("/prever",data="{",content_type="application/json").status_code == 400
    assert client.post("/prever",data="{}").status_code == 415
    assert client.post("/prever",json=[]).status_code == 400
    assert client.post("/prever",json={"historico":[None]*7}).status_code == 400
    assert client.get("/prever").status_code == 405
    assert client.get("/nao-existe").status_code == 404


def test_corpo_grande(client):
    assert client.post("/prever",data='x'*17000,content_type="application/json").status_code == 413


def test_historico_futuro(client,corpo):
    inicio = date.today() + timedelta(days=1)
    for i,linha in enumerate(corpo["historico"]):
        linha["data"] = (inicio+timedelta(days=i)).isoformat()
    assert client.post("/prever",json=corpo).status_code == 400


def test_falha_explicita_modelos_ausentes(tmp_path,corpo):
    cliente = create_app(tmp_path).test_client()
    assert cliente.get("/health").status_code == 503
    assert cliente.post("/prever",json=corpo).status_code == 503
    assert cliente.post("/agrupar",json=corpo).status_code == 503


def test_modelo_alterado_nao_e_carregado(tmp_path,corpo):
    import shutil
    for f in (RAIZ / "modelos").glob("*"):
        shutil.copy(f,tmp_path/f.name)
    (tmp_path / "previsao.joblib").write_bytes(b"arquivo alterado")
    assert create_app(tmp_path).test_client().get("/health").status_code == 503


def test_dias_incompletos_nao_entram_no_treino():
    diario=carregar_diario()
    auditoria=pd.read_csv(RAIZ / "dados/auditoria_diaria.csv",parse_dates=["data"])
    assert len(diario) == 1358
    assert set(diario.data) == set(auditoria.loc[auditoria.dia_completo,"data"])
    assert auditoria.loc[auditoria.dia_completo,"minutos_validos"].eq(1440).all()
    assert auditoria.loc[~auditoria.dia_completo,"consumo_kwh"].isna().all()


def test_janelas_regressao_e_corte_cronologico():
    t=pd.read_csv(RAIZ / "dados/treinamento_regressao.csv",parse_dates=["data_alvo"])
    mapa=carregar_diario().set_index("data").consumo_kwh
    assert t.loc[t.particao.eq("treino"),"data_alvo"].max() < t.loc[t.particao.eq("teste"),"data_alvo"].min()
    for linha in t.itertuples():
        for lag in range(1,8):
            assert np.isclose(getattr(linha,f"lag_{lag}"),mapa.loc[linha.data_alvo-pd.Timedelta(days=lag)])
        assert np.isclose(linha.alvo_kwh,mapa.loc[linha.data_alvo])


def test_escala_ajustada_so_no_treino_e_semanas_sem_sobreposicao():
    t=pd.read_csv(RAIZ / "dados/treinamento_agrupamento.csv",parse_dates=["data_inicio","data_fim"])
    assert ((t.data_fim-t.data_inicio).dt.days == 6).all()
    assert (t.data_inicio.iloc[1:].to_numpy() > t.data_fim.iloc[:-1].to_numpy()).all()
    treino=t.loc[t.particao.eq("treino"),COLUNAS_GRUPO]
    b=carregar_modelos(RAIZ / "modelos")["agrupamento"]
    assert np.allclose(b["modelo"].named_steps["escala"].mean_,treino.mean())


def test_aviso_fora_do_dominio(client,corpo):
    for linha in corpo["historico"]: linha["consumo_kwh"] = 0
    for rota in ["prever","agrupar"]:
        r=client.post("/"+rota,json=corpo)
        assert r.status_code == 200
        assert any("fora da faixa" in a for a in r.json["avisos"])
