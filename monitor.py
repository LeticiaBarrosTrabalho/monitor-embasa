import time
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO = "historico.csv"
INTERVALO = 900

def iniciar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)

def salvar(linha):
    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        f.write(",".join(linha) + "\n")

def extrair(driver):
    driver.get(URL)
    time.sleep(5)

    elementos = driver.find_elements(By.TAG_NAME, "tr")

    dados = []

    for el in elementos:
        texto = el.text.strip()

        if "/" in texto and len(texto) > 20:
            partes = texto.split("\n")

            try:
                codigo = partes[0]
                nome = partes[1]
                status = partes[2]
                data = partes[3]

                objeto = " | ".join(partes)

                link = URL

                dados.append([codigo, nome, objeto, data, link])
            except:
                pass

    return dados

def monitor():
    print("🔎 Monitor com Selenium rodando...")

    vistos = set()
    driver = iniciar_driver()

    while True:
        try:
            itens = extrair(driver)

            for item in itens:
                chave = item[0]

                if chave not in vistos:
                    vistos.add(chave)

                    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                    salvar(item + [agora])

                    print("🚨 Novo completo:", item)

        except Exception as e:
            print("Erro:", e)

        time.sleep(INTERVALO)