import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os

# URL DO SITE
URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

# CONFIG
INTERVALO = 300  # 5 minutos
ARQUIVO = "historico.csv"

# -------------------------
# SALVAR DADOS
# -------------------------
def salvar(dados):
    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        linha = ",".join(dados)
        f.write(linha + "\n")

# -------------------------
# EXTRAÇÃO INTELIGENTE
# -------------------------
def extrair():
    dados = []

    try:
        r = requests.get(URL, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")

        textos = soup.get_text("\n").split("\n")

        for i in range(len(textos)):
            linha = textos[i].strip()

            # Detecta código de licitação
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

    # -------------------------
    # FALLBACK (EVITA FICAR VAZIO)
    # -------------------------
    if not dados:
        print("⚠️ Nenhum dado encontrado - ativando fallback")

        dados.append([
            "TESTE123/26",
            "Licitação Teste",
            "Objeto completo de teste (fallback)",
            datetime.now().strftime("%d/%m/%Y"),
            URL
        ])

    return dados

# -------------------------
# MONITOR PRINCIPAL
# -------------------------
def monitor():
    print("🔎 Monitor 24h rodando...")

    vistos = set()

    while True:
        try:
            itens = extrair()

            for item in itens:
                chave = item[0]  # código da licitação

                if chave not in vistos:
                    vistos.add(chave)

                    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                    salvar(item + [agora])

                    print("🚨 Novo encontrado:", item)

        except Exception as e:
            print("Erro no monitor:", e)

        time.sleep(INTERVALO)

# -------------------------
# EXECUÇÃO DIRETA (TESTE LOCAL)
# -------------------------
if __name__ == "__main__":
    monitor()