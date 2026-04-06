import time
import requests
from plyer import notification

URL = "http://SEU-SERVIDOR/status"

def notify(title, msg):
    notification.notify(
        title=title,
        message=msg,
        timeout=5
    )

def monitor():
    print("🟢 Monitor industrial iniciado")

    ultima_versao = None

    while True:
        try:
            r = requests.get(URL).json()
            versao = r["versao"]

            if ultima_versao is None:
                ultima_versao = versao

            elif versao != ultima_versao:
                notify(
                    "🔔 Sistema Industrial",
                    f"Alteração detectada! v{versao}"
                )
                ultima_versao = versao

        except Exception as e:
            print("Erro:", e)

        time.sleep(10)

monitor()