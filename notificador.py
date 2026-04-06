import requests
import time
import os
from winotify import Notification

URL = "https://monitor-embasa.onrender.com/dados"
ARQUIVO = "controle.txt"

# -------------------------
# CARREGA ÚLTIMO ID
# -------------------------
if os.path.exists(ARQUIVO):
    with open(ARQUIVO, "r") as f:
        ultimo_id = int(f.read().strip())
else:
    ultimo_id = 0

print("🔔 Notificador estável rodando...")

# -------------------------
# LOOP
# -------------------------
while True:
    try:
        print("🔄 Verificando...")

        r = requests.get(URL, timeout=60)
        dados = r.json()

        novos = [d for d in dados if d["id"] > ultimo_id]

        if novos:
            print(f"🚨 {len(novos)} novos registros")

            for item in novos:
                Notification(
                    app_id="Monitor EMBASA",
                    title="🚨 Nova Licitação",
                    msg=f'{item["codigo"]} - {item["nome"]}'
                ).show()

                print("🔔 Notificado:", item["codigo"])

            # salva último ID
            ultimo_id = max(d["id"] for d in dados)

            with open(ARQUIVO, "w") as f:
                f.write(str(ultimo_id))

    except Exception as e:
        print("❌ Erro:", e)

    time.sleep(15)