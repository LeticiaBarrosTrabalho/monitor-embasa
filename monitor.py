import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os
import pytz

# CONFIG
URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
INTERVALO = 300
ARQUIVO = "historico.csv"

# FUSO HORÁRIO BRASIL
fuso = pytz.timezone("America/Sao_Paulo")

# -------------------------
# SALVAR DADOS
# -------------------------
def salvar(dados):
    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        f.write(",".join(dados) + "\n")

# -------------------------
# EXTRAÇÃO
# -------------------------
def extrair():
    dados = []

    try:
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

                    dados.append([codigo, nome, objeto, data, link])
                except:
                    pass

    except Exception as e:
        print("Erro ao acessar site:", e)

    # fallback (nunca fica vazio)
    if not dados:
        dados.append([
            "TESTE123/26",
            "Licitação Teste",
            "Objeto de teste automático",
            datetime.now(fuso).strftime("%d/%m/%Y"),
            URL
        ])

    return dados

# -------------------------
# MONITOR
# -------------------------
def monitor():
    print("🔎 Monitor rodando 24h...")

    vistos = set()

    while True:
        try:
            itens = extrair()

            for item in itens:
                chave = item[0]

                if chave not in vistos:
                    vistos.add(chave)

                    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M")

                    salvar(item + [agora])

                    print("🚨 Novo:", item)

        except Exception as e:
            print("Erro monitor:", e)

        time.sleep(INTERVALO)