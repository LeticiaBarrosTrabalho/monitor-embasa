import time
import requests
from datetime import datetime
import os
import re

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO_LOG = "historico.txt"
ARQUIVO_ESTADO = "estado.txt"

INTERVALO = 900  # 15 minutos

def salvar_log(msg):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def salvar_estado(itens):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        f.write("\n".join(itens))

def monitor():
    print("🔎 Monitor rodando 24h...")

    while True:
        try:
            r = requests.get(URL, timeout=30)
            html = r.text.lower()

            codigos = ["TESTE123/26"]

            itens_atuais = set()

            for c in codigos[:10]:
                link = URL
                objeto = "ver no site"

                item = f"{c} | {objeto} | {link}"
                itens_atuais.add(item)

            antigos = carregar_estado()
            novos = itens_atuais - antigos

            if novos:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                for item in novos:
                    msg = f"{item} | {agora}"
                    print("🚨 Nova licitação:", msg)
                    salvar_log(msg)

                salvar_estado(itens_atuais)

        except Exception as e:
            print("Erro:", e)

        time.sleep(INTERVALO)

if __name__ == "__main__":
    monitor()