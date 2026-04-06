import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pytz
from database import conectar, criar_tabela

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
fuso = pytz.timezone("America/Sao_Paulo")

criar_tabela()

def salvar(item):
    conn = conectar()
    cursor = conn.cursor()

    # evita duplicado
    cursor.execute("SELECT * FROM licitacoes WHERE codigo = ?", (item[0],))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute("""
    INSERT INTO licitacoes (codigo, nome, objeto, data, link, registro)
    VALUES (?, ?, ?, ?, ?, ?)
    """, item)

    conn.commit()
    conn.close()
    return True

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

                dados.append([
                    codigo,
                    nome,
                    objeto,
                    data,
                    link,
                    datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
                ])
            except:
                pass

    return dados

print("🔎 Monitor 24h rodando...")

while True:
    try:
        itens = extrair()

        for item in itens:
            if salvar(item):
                print("🚨 Novo:", item)

    except Exception as e:
        print("Erro:", e)

    time.sleep(300)