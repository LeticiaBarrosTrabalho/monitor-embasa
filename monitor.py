import time
import requests
import pandas as pd
from plyer import notification
import os

URL = "https://monitor-embasa.onrender.com/dados"
ARQUIVO_LOCAL = "vistos.txt"

if os.path.exists(ARQUIVO_LOCAL):
    with open(ARQUIVO_LOCAL, "r") as f:
        vistos = set(f.read().splitlines())
else:
    vistos = set()

while True:
    try:
        df = pd.read_json(URL)

        novos = []

        for _, row in df.iterrows():
            codigo = str(row["codigo"])

            if codigo not in vistos:
                vistos.add(codigo)
                novos.append(row)

        with open(ARQUIVO_LOCAL, "w") as f:
            for v in vistos:
                f.write(v + "\n")

        for row in novos:
            notification.notify(
                title="🚨 Nova Licitação",
                message=f'{row["codigo"]} | {row["nome"]}',
                timeout=10
            )

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)