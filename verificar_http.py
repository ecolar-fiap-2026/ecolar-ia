"""Teste HTTP real autocontido: inicia servidor temporário e encerra ao terminar."""
import json
import threading
import urllib.request
import urllib.error
from werkzeug.serving import make_server
from app import create_app
from ecolar_ia.dados import RAIZ


def verificar():
    servidor = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{servidor.server_port}"
    corpo = (RAIZ / "exemplos/requisicao.json").read_bytes()
    resultados = []
    try:
        for rota in ["/", "/health", "/prever", "/agrupar"]:
            req = urllib.request.Request(base + rota, data=corpo if rota in ["/prever","/agrupar"] else None,
                                         headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=15) as resposta:
                assert resposta.status == 200
                conteudo = resposta.read().decode()
                dado = json.loads(conteudo) if rota != "/" else {"pagina_teste": "Prever próximo dia" in conteudo}
                resultados.append({"rota":rota,"status":resposta.status,"resposta":dado})
        req = urllib.request.Request(base + "/prever", data=b'{"historico":[]}',
                                     headers={"Content-Type":"application/json"})
        try:
            urllib.request.urlopen(req,timeout=15)
            raise AssertionError("Entrada inválida deveria retornar HTTP 400.")
        except urllib.error.HTTPError as erro:
            assert erro.code == 400
            resultados.append({"rota":"/prever (histórico vazio)","status":erro.code,
                               "resposta":json.loads(erro.read())})
        (RAIZ / "resultados/teste_http.json").write_text(
            json.dumps({"metodo":"Servidor Werkzeug temporário e urllib via loopback TCP real",
                        "resultados":resultados},indent=2,ensure_ascii=False),encoding="utf-8")
        print("HTTP real: página, health, previsão e agrupamento HTTP 200; entrada inválida HTTP 400.")
    finally:
        servidor.shutdown()
        servidor.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    verificar()
