import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

INTERVALO = 900  # 15 min
ARQUIVO = "historico.csv"

def salvar(dados):
    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        f.write(",".join(dados) + "\n")

def extrair():
    r = requests.get(URL, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    textos = soup.get_text("\n").split("\n")

    dados = []
    i = 0

    while i < len(textos):
        linha = textos[i].strip().lower()

        if "/" in linha and len(linha) < 15:
            codigo = linha

            try:
                nome = textos[i+1].strip()
                status = textos[i+2].strip()
                data = textos[i+3].strip()

                objeto = f"{nome} - {status}"

                link = URL

                dados.append([codigo, nome, objeto, data, link])
            except:
                pass

        i += 1

    return dados

def monitor():
    vistos = set()

    print("🔎 Monitor avançado rodando...")

    while True:
        try:
            itens = extrair()

            for item in itens:
                chave = item[0]

                if chave not in vistos:
                    vistos.add(chave)

                    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                    salvar(item + [agora])

                    print("🚨 Novo:", item)

        except Exception as e:
            print("Erro:", e)

        time.sleep(INTERVALO)

if __name__ == "__main__":
    monitor()