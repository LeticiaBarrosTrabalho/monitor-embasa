import requests
import time
from winotify import Notification

URL = "https://monitor-embasa.onrender.com/dados"
vistos = set()

print("🔔 Notificador rodando...")

while True:
    try:
        r = requests.get(URL, timeout=30)
        dados = r.json()

        for item in dados:
            chave = item["id"]

            if chave not in vistos:
                vistos.add(chave)

                Notification(
                    app_id="Monitor EMBASA",
                    title="🚨 Nova Licitação",
                    msg=f'{item["codigo"]} - {item["nome"]}'
                ).show()

                print("🔔 Novo:", item["codigo"])

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)