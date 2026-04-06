import time
import requests
from plyer import notification

BASE_URL = "http://127.0.0.1:5000"

def windows_notify(titulo, msg):
    notification.notify(
        title=titulo,
        message=msg,
        timeout=5
    )

def enviar_evento(msg):
    try:
        requests.get(f"{BASE_URL}/evento/{msg}")
    except:
        pass

def monitorar():
    print("🟢 Monitor industrial iniciado")

    estado_anterior = None

    while True:
        try:
            # simulação de checagem (substitua sua regra real aqui)
            r = requests.get("https://httpbin.org/get")
            estado_atual = r.status_code

            if estado_atual != estado_anterior:
                print("📡 Mudança detectada")

                enviar_evento("ALTERAÇÃO DETECTADA NO SISTEMA")

                windows_notify(
                    "Sistema Industrial",
                    "Alteração detectada com sucesso"
                )

                estado_anterior = estado_atual

        except Exception as e:
            print("Erro:", e)

        time.sleep(10)

monitorar()