import time
import requests
from plyer import notification

URL = "http://127.0.0.1:5000/teste-notificacao"

def notificar(titulo, mensagem):
    notification.notify(
        title=titulo,
        message=mensagem,
        timeout=5
    )

def monitorar():
    print("🔎 Monitor rodando...")

    ultimo_estado = None

    while True:
        try:
            resposta = requests.get("https://httpbin.org/get")
            estado_atual = resposta.status_code

            if estado_atual != ultimo_estado:
                print("📢 Mudança detectada!")

                requests.get(URL)

                notificar(
                    "Monitor EMBASA",
                    "🔔 Alteração detectada no sistema"
                )

                ultimo_estado = estado_atual

        except Exception as e:
            print("Erro:", e)

        time.sleep(10)

monitorar()