import time
import requests
from bs4 import BeautifulSoup
from plyer import notification

URL_SITE = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
URL_API = "https://monitor-embasa.onrender.com/novo"
URL_DADOS = "https://monitor-embasa.onrender.com/dados"

vistos = set()

def notificar(msg):
    notification.notify(
        title="🚨 EMBASA",
        message=msg,
        timeout=5
    )

# 🔁 recuperar alterações antigas (PC desligado)
def recuperar_antigos():
    try:
        dados = requests.get(URL_DADOS).json()

        for item in dados[:5]:
            notificar(f"Atualização anterior: {item['codigo']}")
    except:
        pass

def extrair():
    r = requests.get(URL_SITE, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    textos = soup.get_text("\n").split("\n")
    dados = []

    for i in range(len(textos)):
        linha = textos[i].strip()

        if "/" in linha and len(linha) < 15:
            try:
                codigo = linha
                nome = textos[i+1].strip()
                status = textos[i+2].strip()
                data = textos[i+3].strip()

                objeto = f"{nome} | {status}"

                dados.append({
                    "codigo": codigo,
                    "nome": nome,
                    "objeto": objeto,
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
                chave = item["codigo"]

                if chave not in vistos:
                    vistos.add(chave)

                    requests.post(URL_API, json=item)

                    notificar(f"{item['codigo']} - {item['nome']}")

        except Exception as e:
            print("Erro:", e)

        time.sleep(60)

monitor()