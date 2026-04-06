import time
import requests

URL = "http://127.0.0.1:5000/teste"

def monitorar():
    print("🔎 Monitor iniciado...")

    ultimo_estado = None

    while True:
        try:
            # simulação de mudança (substituir sua lógica real aqui)
            resposta = requests.get("https://httpbin.org/get")

            estado_atual = resposta.status_code

            if estado_atual != ultimo_estado:
                print("📢 Mudança detectada!")

                requests.get(URL)

                ultimo_estado = estado_atual

        except Exception as e:
            print("Erro:", e)

        time.sleep(10)


monitorar()