"""Alternativa aos notebooks: recria os dois modelos a partir dos CSVs incluídos."""
from ecolar_ia.treino import treinar_regressao, treinar_agrupamento, registrar_ambiente

if __name__ == "__main__":
    a,_ = treinar_regressao()
    b,_ = treinar_agrupamento()
    registrar_ambiente()
    print("Regressão:", a["teste_modelo"])
    print("Agrupamento:", b["qualidade_teste"])
    print("Modelos exportados na pasta modelos.")
