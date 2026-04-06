import time
import requests
import pandas as pd
from plyer import notification
import os

URL = "https://monitor-embasa.onrender.com/dados"

ARQUIVO_LOCAL = "vistos.txt"

# Carrega já vistos (IMPORTANTE)
if os.path.exists(ARQUIVO_LOCAL):
    with open(ARQUIVO_LOCAL, "r") as f:
        vistos = set(f.read().splitlines())
else:
    vistos = set()

print("🔔 Notificador rodando em segundo plano...")

while True:
    try:
        df = pd.read_json(URL)

        novos = []

        for _, row in df.iterrows():
            codigo = str(row["codigo"])

            if codigo not in vistos:
                vistos.add(codigo)
                novos.append(row)

        # Salva histórico local (EVITA DUPLICAÇÃO)
        with open(ARQUIVO_LOCAL, "w") as f:
            for item in vistos:
                f.write(item + "\n")

        # 🔔 Notifica
        for row in novos:
            mensagem = f'{row["codigo"]} | {row["nome"]}'

            notification.notify(
                title="🚨 Nova Licitação EMBASA",
                message=mensagem,
                timeout=10
            )

            print("🔔 Nova:", mensagem)

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)