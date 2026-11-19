"""Preparo reproduzível da fonte UCI; download não é necessário para usar a API."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
import urllib.request
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
URL = "https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip"


def preparar(arquivo_zip=None):
    destino = RAIZ / "dados"
    destino.mkdir(exist_ok=True)
    arquivo_zip = Path(arquivo_zip) if arquivo_zip else destino / "original_uci.zip"
    if not arquivo_zip.exists():
        print("Baixando fonte oficial UCI (cerca de 20 MB)...")
        with urllib.request.urlopen(URL, timeout=120) as r:
            arquivo_zip.write_bytes(r.read())
    sha = hashlib.sha256(arquivo_zip.read_bytes()).hexdigest()
    with zipfile.ZipFile(arquivo_zip) as z:
        with z.open("household_power_consumption.txt") as f:
            bruto = pd.read_csv(f, sep=";", usecols=["Date", "Time", "Global_active_power"],
                                na_values=["?"], dtype={"Global_active_power":float})
    bruto["instante"] = pd.to_datetime(bruto["Date"] + " " + bruto["Time"], format="%d/%m/%Y %H:%M:%S")
    if bruto["instante"].duplicated().any():
        raise ValueError("Instantes duplicados na fonte: revisão necessária.")
    bruto = bruto.sort_values("instante").set_index("instante")
    potencia = bruto["Global_active_power"]
    potencia = potencia.where(np.isfinite(potencia) & (potencia >= 0))
    grupos = potencia.resample("D")
    diario = pd.DataFrame({"minutos_validos":grupos.count(),
                           "consumo_parcial_kwh":grupos.sum(min_count=1) / 60})
    diario.index.name = "data"
    diario["dia_completo"] = diario["minutos_validos"].eq(1440)
    # Cada média de potência em kW corresponde a um minuto: energia = kW / 60.
    # Não extrapolar somas parciais nem imputar ausências com zero.
    diario["consumo_kwh"] = diario["consumo_parcial_kwh"].where(diario["dia_completo"])
    diario.reset_index().to_csv(destino / "auditoria_diaria.csv", index=False, float_format="%.9f")
    completo = diario.loc[diario.dia_completo, ["consumo_kwh"]].reset_index()
    completo.to_csv(destino / "consumo_diario_uci.csv", index=False, float_format="%.9f")
    manifest = {"fonte":"UCI Individual Household Electric Power Consumption",
                "url":URL, "doi":"10.24432/C58K54", "licenca":"CC BY 4.0",
                "autores":"Georges Hebrail e Alice Berard", "consulta":"2026-11-11",
                "sha256_zip_original":sha, "linhas_minuto":len(bruto),
                "dias_calendario":len(diario), "dias_completos":len(completo),
                "dias_excluidos":int((~diario.dia_completo).sum()),
                "periodo_original":[str(bruto.index.min()),str(bruto.index.max())],
                "regra":"Somar Global_active_power / 60 por dia; aceitar somente 1440 minutos válidos.",
                "limite":"Uma casa francesa de 2006-2010; sem validação de generalização para o Brasil."}
    (destino / "fonte.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return completo


def carregar_diario():
    return pd.read_csv(RAIZ / "dados/consumo_diario_uci.csv", parse_dates=["data"])
