import time
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO_LOG = "historico.txt"
ARQUIVO_ESTADO = "estado.txt"

PALAVRAS = ["sapiranga", "dragagem", "ete"]

def salvar_log(msg):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def salvar_estado(itens):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        f.write("\n".join(itens))

def extrair_objeto(pagina):
    linhas = pagina.split("\n")
    for i, linha in enumerate(linhas):
        if any(p in linha for p in ["objeto", "descrição", "referente", "finalidade"]):
            return " ".join(linhas[i:i+2])[:300]
    return ""

def monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print("🔎 Monitor rodando...")

    while True:
        try:
            driver.get(URL)
            time.sleep(5)

            texto = driver.find_element("tag name", "body").text.lower()
            linhas = [l.strip() for l in texto.split("\n") if l.strip()]

            registros = []

            for i in range(len(linhas)):
                linha = linhas[i]

                if "/" in linha and any(c.isdigit() for c in linha):
                    codigo = linha
                    data_str = linhas[i+3] if i+3 < len(linhas) else ""

                    try:
                        data = datetime.strptime(data_str, "%d/%m/%Y")
                    except:
                        continue

                    registros.append({
                        "codigo": codigo,
                        "data": data,
                        "data_str": data_str
                    })

            registros.sort(key=lambda x: x["data"], reverse=True)
            registros = registros[:10]

            itens_atuais = set()
            elementos = driver.find_elements("tag name", "a")

            for r in registros:
                codigo = r["codigo"]
                data_str = r["data_str"]

                link = ""

                for el in elementos:
                    if codigo in el.text.lower():
                        link = el.get_attribute("href")
                        break

                objeto = ""

                if link:
                    try:
                        driver.execute_script("window.open(arguments[0]);", link)
                        driver.switch_to.window(driver.window_handles[1])

                        time.sleep(3)

                        pagina = driver.find_element("tag name", "body").text.lower()
                        objeto = extrair_objeto(pagina)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except:
                        pass

                item = f"{codigo} | {data_str} | {objeto} | {link}"
                itens_atuais.add(item.lower())

            antigos = carregar_estado()
            novos = itens_atuais - antigos

            if novos:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                for item in novos:
                    if any(p in item for p in PALAVRAS):
                        msg = f"{item} | {agora}"
                        print("🚨 Nova licitação:", msg)
                        salvar_log(msg)

                salvar_estado(itens_atuais)

        except Exception as e:
            print("Erro:", e)

        time.sleep(600)

if __name__ == "__main__":
    monitor()