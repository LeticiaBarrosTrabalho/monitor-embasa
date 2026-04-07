import time
import requests
from bs4 import BeautifulSoup
from plyer import notification

URL_SITE = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
URL_API = "https://monitor-embasa.onrender.com/novo"
URL_DADOS = "https://monitor-embasa.onrender.com/dados"

vistos = set()

def notificar(msg):
    try:
        notification.notify(
            title="🚨 EMBASA",
            message=msg,
            timeout=10
        )
    except:
        pass

def recuperar_antigos():
    try:
        dados = requests.get(URL_DADOS, timeout=20).json()
        for item in dados[:5]:
            notificar(f"Anterior: {item['codigo']}")
    except:
        pass

def extrair():
    r = requests.get(URL_SITE, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    textos = soup.get_text("\n").split("\n")
    dados = []

    for i in range(len(textos)):
        linha = textos[i].strip()

        if "/" in linha and len(linha) < 20:
            try:
                codigo = linha
                nome = textos[i+1].strip()
                status = textos[i+2].strip()
                data = textos[i+3].strip()

                dados.append({
                    "codigo": codigo,
                    "nome": nome,
                    "objeto": f"{nome} | {status}",
                    "data": data,
                    "link": URL_SITE
                })
            except:
                pass

    return dados

def monitor():
    print("🟢 Monitor rodando...")

    recuperar_antigos()

    while True:
        try:
            itens = extrair()

            for item in itens:
                if item["codigo"] not in vistos:
                    vistos.add(item["codigo"])

                    requests.post(URL_API, json=item, timeout=20)

                    notificar(f"{item['codigo']} - {item['nome']}")

        except Exception as e:
            print("Erro:", e)

        time.sleep(60)

monitor()