import time
import requests
from plyer import notification
from bs4 import BeautifulSoup

URL = "https://monitor-embasa.onrender.com"

vistos = set()

print("🔔 Notificador rodando...")

while True:
    try:
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")

        linhas = soup.find_all("tr")

        novos = []

        for linha in linhas[1:]:
            colunas = linha.find_all("td")

            if len(colunas) >= 5:
                codigo = colunas[0].text.strip()
                nome = colunas[1].text.strip()
                objeto = colunas[2].text.strip()
                data = colunas[3].text.strip()

                chave = codigo + data

                if chave not in vistos:
                    novos.append((codigo, nome, objeto))
                    vistos.add(chave)

        # 🔥 AGORA NOTIFICA TUDO QUE NÃO FOI VISTO
        for item in novos:
            codigo, nome, objeto = item

            mensagem = f"{codigo} | {nome} | {objeto}"

            notification.notify(
                title="🚨 Nova Licitação",
                message=mensagem[:200],
                timeout=10
            )

            print("🔔 Nova detectada:", mensagem)

    except Exception as e:
        print("Erro:", e)

    time.sleep(10)