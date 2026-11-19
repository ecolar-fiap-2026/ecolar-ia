"""Mesmas transformações para treinamento e API; nenhum dado futuro como entrada."""
from datetime import date, timedelta
import math
import numpy as np
import pandas as pd

COLUNAS_REGRESSAO = [f"lag_{i}" for i in range(7, 0, -1)] + [
    "dia_semana_seno", "dia_semana_cosseno", "mes_seno", "mes_cosseno"
]
COLUNAS_GRUPO = ["media_kwh", "desvio_kwh", "minimo_kwh", "maximo_kwh",
                 "media_dias_uteis_kwh", "media_fim_semana_kwh"]


def atributos_regressao(valores, data_alvo):
    """Sete dias do mais antigo ao mais recente + calendário do dia previsto."""
    d = pd.Timestamp(data_alvo)
    return list(map(float, valores)) + [
        math.sin(2 * math.pi * d.dayofweek / 7),
        math.cos(2 * math.pi * d.dayofweek / 7),
        math.sin(2 * math.pi * (d.month - 1) / 12),
        math.cos(2 * math.pi * (d.month - 1) / 12),
    ]


def atributos_grupo(valores, datas):
    v = np.asarray(valores, dtype=float)
    fim_semana = np.array([pd.Timestamp(d).dayofweek >= 5 for d in datas])
    return [float(v.mean()), float(v.std(ddof=0)), float(v.min()), float(v.max()),
            float(v[~fim_semana].mean()), float(v[fim_semana].mean())]


def tabela_regressao(diario):
    """Exclui janelas com qualquer dia ausente, sem preencher consumo com zero."""
    mapa = diario.set_index("data")["consumo_kwh"]
    linhas = []
    for alvo in diario["data"]:
        datas = pd.date_range(alvo - pd.Timedelta(days=7), periods=7)
        if all(d in mapa.index for d in datas):
            valores = mapa.loc[datas].to_numpy()
            linhas.append([alvo, *atributos_regressao(valores, alvo), float(mapa.loc[alvo])])
    return pd.DataFrame(linhas, columns=["data_alvo", *COLUNAS_REGRESSAO, "alvo_kwh"])


def tabela_grupos(diario):
    """Semanas completas segunda-domingo, sem sobreposição entre amostras."""
    mapa = diario.set_index("data")["consumo_kwh"]
    linhas = []
    for inicio in diario["data"]:
        if inicio.dayofweek != 0:
            continue
        datas = pd.date_range(inicio, periods=7)
        if all(d in mapa.index for d in datas):
            v = mapa.loc[datas].to_numpy()
            linhas.append([inicio, datas[-1], *atributos_grupo(v, datas)])
    return pd.DataFrame(linhas, columns=["data_inicio", "data_fim", *COLUNAS_GRUPO])


class EntradaInvalida(ValueError):
    """Erro de contrato público, seguro para mostrar ao usuário."""


def validar_historico(corpo):
    """Aceita exatamente sete dias consecutivos, ISO e kWh não negativos."""
    if not isinstance(corpo, dict) or set(corpo) != {"historico"}:
        raise EntradaInvalida('Envie somente o campo "historico" com sete registros.')
    h = corpo["historico"]
    if not isinstance(h, list) or len(h) != 7:
        raise EntradaInvalida("O histórico precisa ter exatamente sete dias consecutivos.")
    datas, valores = [], []
    for item in h:
        if not isinstance(item, dict) or set(item) != {"data", "consumo_kwh"}:
            raise EntradaInvalida("Cada registro deve conter data e consumo_kwh.")
        s = item["data"]
        try:
            if not isinstance(s, str) or len(s) != 10:
                raise ValueError()
            d = date.fromisoformat(s)
            if d.isoformat() != s or not 1900 <= d.year <= 2200:
                raise ValueError()
        except ValueError:
            raise EntradaInvalida("Data inválida: use AAAA-MM-DD entre 1900 e 2200.") from None
        if d > date.today():
            raise EntradaInvalida("O histórico não pode conter datas futuras em relação ao servidor.")
        v = item["consumo_kwh"]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise EntradaInvalida("consumo_kwh deve ser número JSON, não texto ou booleano.")
        try:
            v = float(v)
        except (OverflowError, ValueError):
            raise EntradaInvalida("Consumo fora do intervalo numérico.") from None
        if not math.isfinite(v) or not 0 <= v <= 10000:
            raise EntradaInvalida("Consumo deve estar entre 0 e 10000 kWh/dia e ser finito.")
        if datas and d != datas[-1] + timedelta(days=1):
            raise EntradaInvalida("Datas devem estar em ordem crescente, sem lacunas ou duplicatas.")
        datas.append(d)
        valores.append(v)
    return datas, valores
