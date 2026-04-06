import requests
import time
from winotify import Notification

URL = "https://monitor-embasa.onrender.com/dados"
ultimo_id = 0

print("🔔 Notificador iniciado...")

while True:
    try:
        r = requests.get(URL, timeout=30)
        dados = r.json()

        if not dados:
            print("Sem dados")
            time.sleep(10)
            continue

        maior_id = max(d["id"] for d in dados)

        if maior_id > ultimo_id:

            novos = [d for d in dados if d["id"] > ultimo_id]

            for n in novos:
                Notification(
                    app_id="Monitor EMBASA",
                    title="🚨 Nova Licitação",
                    msg=f'{n["codigo"]} - {n["nome"]}'
                ).show()

                print("Notificado:", n["codigo"])

            ultimo_id = maior_id

        else:
            print("Sem novidades")

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)