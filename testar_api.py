"""Cliente HTTP real: deixe app.py aberto em outro terminal antes de executar."""
import json
import urllib.request
import urllib.error
from pathlib import Path

if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent
    corpo = (raiz / "exemplos/requisicao.json").read_bytes()
    for rota in ["health", "prever", "agrupar"]:
        req = urllib.request.Request("http://127.0.0.1:5000/" + rota,
                                     data=corpo if rota != "health" else None,
                                     headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                print("\n",rota,"HTTP",r.status)
                print(json.dumps(json.load(r), ensure_ascii=False, indent=2))
        except urllib.error.HTTPError as erro:
            raise SystemExit(f"API retornou HTTP {erro.code}: {erro.read().decode()}") from None
        except urllib.error.URLError:
            raise SystemExit("Não foi possível conectar. Deixe app.py aberto em outro terminal na porta 5000.") from None
