import time
import requests
from plyer import notification

URL = "https://monitor-embasa.onrender.com"

vistos = set()

while True:
    try:
        r = requests.get(URL)
        html = r.text

        blocos = html.split('<tr>')[1:]

        for b in blocos:
            texto = b.split('</tr>')[0]

            if texto not in vistos:
                vistos.add(texto)

                notification.notify(
                    title="Nova Licitação",
                    message=texto,
                    timeout=10
                )

                print("🔔 Nova:", texto)

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)