import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from database import conectar
import pytz

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
fuso = pytz.timezone("America/Sao_Paulo")

def extrair():
    dados = []

    r = requests.get(URL, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    textos = soup.get_text("\n").split("\n")

    for i in range(len(textos)):
        linha = textos[i].strip()

        if "/" in linha and len(linha) < 15:
            try:
                codigo = linha
                nome = textos[i+1].strip()
                status = textos[i+2].strip()
                data = textos[i+3].strip()

                objeto = f"{nome} | {status}"
                link = URL

                dados.append((codigo, nome, objeto, data, link))
            except:
                pass

    return dados

def monitor():
    vistos = set()

    while True:
        try:
            itens = extrair()

            conn = conectar()
            cursor = conn.cursor()

            for item in itens:
                if item[0] not in vistos:
                    vistos.add(item[0])

                    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

                    cursor.execute("""
                    INSERT INTO licitacoes (codigo, nome, objeto, data, link, registro)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, item + (agora,))

                    print("Novo:", item[0])

            conn.commit()
            conn.close()

        except Exception as e:
            print("Erro:", e)

        time.sleep(300)

monitor()