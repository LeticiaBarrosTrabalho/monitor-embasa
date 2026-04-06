import time
import requests
from plyer import notification
import pandas as pd

URL = "https://monitor-embasa.onrender.com/dados"

vistos = set()

print("🔔 Notificador rodando em segundo plano...")

while True:
    try:
        df = pd.read_json(URL)

        novos = []

        for _, row in df.iterrows():
            chave = row["codigo"]

            if chave not in vistos:
                vistos.add(chave)
                novos.append(row)

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

    time.sleep(15)