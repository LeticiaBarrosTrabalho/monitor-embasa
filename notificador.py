import requests
import time
import os
from winotify import Notification

URL = "https://monitor-embasa.onrender.com/dados"
ARQUIVO = "controle.txt"

if os.path.exists(ARQUIVO):
    with open(ARQUIVO) as f:
        ultimo = int(f.read().strip())
else:
    ultimo = 0

print("🔔 Notificador rodando...")

while True:
    try:
        r = requests.get(URL, timeout=60)
        dados = r.json()

        novos = [d for d in dados if d["id"] > ultimo]

        if novos:
            for n in novos:
                Notification(
                    app_id="EMBASA",
                    title="Nova Licitação",
                    msg=f'{n["codigo"]} - {n["nome"]}'
                ).show()

            ultimo = max(d["id"] for d in dados)

            with open(ARQUIVO, "w") as f:
                f.write(str(ultimo))

    except Exception as e:
        print("Erro:", e)

    time.sleep(15)