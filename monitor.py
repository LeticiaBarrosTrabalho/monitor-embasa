import time
import requests
from datetime import datetime
import os
import re

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO_LOG = "historico.txt"
ARQUIVO_ESTADO = "estado.txt"

PALAVRAS = ["sapiranga", "dragagem", "ete"]

# -------------------------
# UTIL
# -------------------------

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

# -------------------------
# EXTRAIR DADOS
# -------------------------

def extrair_registros(texto):
    linhas = [l.strip().lower() for l in texto.split("\n") if l.strip()]

    registros = []

    for i in range(len(linhas)):
        linha = linhas[i]

        if "/" in linha and any(c.isdigit() for c in linha):
            codigo = linha

            try:
                data_str = linhas[i+3]
                data = datetime.strptime(data_str, "%d/%m/%Y")
            except:
                continue

            registros.append({
                "codigo": codigo,
                "data": data,
                "data_str": data_str
            })

    registros.sort(key=lambda x: x["data"], reverse=True)
    return registros[:10]

# -------------------------
# MONITOR
# -------------------------

def monitor():
    print("🔎 Monitor rodando (SEM SELENIUM)...")

    while True:
        try:
            r = requests.get(URL, timeout=30)
            texto = r.text.lower()

            registros = extrair_registros(texto)

            itens_atuais = set()

            for r in registros:
                codigo = r["codigo"]
                data_str = r["data_str"]

                # tenta capturar link
                link_match = re.search(r'href="([^"]+)"[^>]*>' + re.escape(codigo), texto)
                link = link_match.group(1) if link_match else ""

                objeto = ""

                item = f"{codigo} | {data_str} | {objeto} | {link}"
                itens_atuais.add(item)

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

        time.sleep(600)  # 10 minutos

# -------------------------
# START
# -------------------------

if __name__ == "__main__":
    monitor()