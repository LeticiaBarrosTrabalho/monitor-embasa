import time
import requests
from plyer import notification
from bs4 import BeautifulSoup
import os

URL = "https://monitor-embasa.onrender.com"

# 🔒 Evita múltiplas execuções
lock_file = "lock_notificador.txt"

if os.path.exists(lock_file):
    print("⚠️ Notificador já está rodando.")
    exit()

open(lock_file, "w").close()

vistos = set()

print("🔔 Notificador rodando...")

try:
    while True:
        try:
            r = requests.get(URL, timeout=10)
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

                    # 🔥 CHAVE ÚNICA (corrige instabilidade)
                    chave = f"{codigo}-{nome}-{objeto}-{data}"
                    chave = chave.strip().lower()

                    if chave not in vistos:
                        novos.append((codigo, nome, objeto))
                        vistos.add(chave)

            # 🔔 Dispara notificações
            for codigo, nome, objeto in novos:
                mensagem = f"{codigo} | {nome} | {objeto}"

                notification.notify(
                    title="🚨 Nova Licitação",
                    message=mensagem[:200],
                    timeout=10
                )

                print("🔔 Nova detectada:", mensagem)

        except Exception as e:
            print("Erro na leitura:", e)

        time.sleep(10)

finally:
    # 🔓 Libera lock se encerrar
    if os.path.exists(lock_file):
        os.remove(lock_file)