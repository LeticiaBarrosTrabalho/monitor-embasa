import time
import requests
import os
import json
from winotify import Notification, audio

# 🔗 API do seu site
URL = "https://monitor-embasa.onrender.com/dados"

# 📁 Arquivo de controle (evita repetir notificações)
ARQUIVO_LOCAL = "vistos.txt"

# -------------------------
# CARREGA HISTÓRICO
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
        print("🔄 Verificando servidor...")

        try:
            # 🔥 timeout alto (Render pode estar dormindo)
            r = requests.get(URL, timeout=60)
            print("✅ Conectado!")
        except requests.exceptions.ReadTimeout:
            print("⏳ Servidor dormindo... tentando novamente...")
            time.sleep(15)
            continue
        except Exception as e:
            print("❌ Erro conexão:", e)
            time.sleep(15)
            continue

        # 🔍 Converte JSON
        try:
            dados = json.loads(r.text)
        except Exception as e:
            print("❌ Erro ao ler JSON:", e)
            time.sleep(10)
            continue

        print(f"📡 Registros recebidos: {len(dados)}")

        novos = []

        # -------------------------
        # DETECTA NOVOS
        # -------------------------
        for row in dados:
            codigo = str(row.get("codigo", "")).strip()
            registro = str(row.get("registro", "")).strip()

            if not codigo:
                continue

            # 🔥 chave única (ESSENCIAL)
            chave = f"{codigo}-{registro}"

            if chave not in vistos:
                vistos.add(chave)
                novos.append(row)

        # -------------------------
        # SALVA CONTROLE LOCAL
        # -------------------------
        with open(ARQUIVO_LOCAL, "w", encoding="utf-8") as f:
            for item in vistos:
                f.write(item + "\n")

        # -------------------------
        # ENVIA NOTIFICAÇÃO
        # -------------------------
        for row in novos:
            mensagem = f'{row.get("codigo","")} | {row.get("nome","")}'

            try:
                toast = Notification(
                    app_id="Monitor EMBASA",
                    title="🚨 Nova Licitação",
                    msg=mensagem,
                    duration="short"
                )

                toast.set_audio(audio.Default, loop=False)
                toast.show()

                print("🔔 Nova detectada:", mensagem)

            except Exception as e:
                print("❌ Erro ao notificar:", e)

    except Exception as e:
        print("❌ Erro geral:", e)

    # ⏱ intervalo (10 segundos)
    time.sleep(10)