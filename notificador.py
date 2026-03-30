import time
from plyer import notification

ARQUIVO = "historico.txt"
ultimo = ""

while True:
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            linhas = f.readlines()

        if linhas:
            ultima = linhas[-1]

            if ultima != ultimo:
                notification.notify(
                    title="Nova Licitação",
                    message=ultima,
                    timeout=10
                )
                ultimo = ultima

    except:
        pass

    time.sleep(60)