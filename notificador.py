import time
import requests
import os
import json
from winotify import Notification, audio

# 🔗 URL da API do seu sistema no Render
URL = "https://monitor-embasa.onrender.com/dados"

# 📁 Arquivo local para controle de notificações já vistas
ARQUIVO_LOCAL = "vistos.txt"

# -------------------------
# CARREGA HISTÓRICO LOCAL
# -------------------------
if os.path.exists(ARQUIVO_LOCAL):
    with open(ARQUIVO_LOCAL, "r", encoding="utf-8") as f:
        vistos = set(f.read().splitlines())
else:
    vistos = set()

print("🔔 Notificador rodando em segundo plano...")

# -------------------------
# LOOP PRINCIPAL
# -------------------------
while True:
    try:
        # 🔄 Requisição para API
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            print("Erro API:", r.status_code)
            time.sleep(10)
            continue

        # ✅ Corrige problema do pandas
        dados = json.loads(r.text)

        novos = []

        # 🔍 Detecta novos registros
        for row in dados:
            codigo = str(row.get("codigo", "")).strip()

            if codigo and codigo not in vistos:
                vistos.add(codigo)
                novos.append(row)

        # 💾 Salva controle local
        with open(ARQUIVO_LOCAL, "w", encoding="utf-8") as f:
            for item in vistos:
                f.write(item + "\n")

        # 🔔 Dispara notificações
        for row in novos:
            mensagem = f'{row.get("codigo","")} | {row.get("nome","")}'

            toast = Notification(
                app_id="Monitor EMBASA",
                title="🚨 Nova Licitação EMBASA",
                msg=mensagem,
                duration="short"
            )

            toast.set_audio(audio.Default, loop=False)
            toast.show()

            print("🔔 Nova detectada:", mensagem)

    except Exception as e:
        print("Erro no notificador:", e)

    # ⏱ Intervalo de verificação
    time.sleep(10)