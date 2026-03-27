import time
import requests
from plyer import notification
import re
import os

URL = "COLE_AQUI_SEU_LINK_DO_RENDER"
ARQUIVO = "ultimo.txt"

def limpar(html):
    return re.sub('<.*?>', '', html)

def carregar():
    if os.path.exists(ARQUIVO):
        return open(ARQUIVO).read()
    return ""

def salvar(v):
    with open(ARQUIVO, "w") as f:
        f.write(v)

ultimo = carregar()

while True:
    try:
        r = requests.get(URL)
        texto = limpar(r.text)

        linhas = [l.strip() for l in texto.split("\n") if l.strip()]

        if linhas:
            atual = linhas[0]

            if atual != ultimo:
                notification.notify(
                    title="Nova Licitação",
                    message=atual[:200],
                    timeout=10
                )
                salvar(atual)
                ultimo = atual

    except:
        pass

    time.sleep(60)