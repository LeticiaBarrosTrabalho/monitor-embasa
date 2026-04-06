from flask import Flask, request, redirect
import pandas as pd
import os
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

ARQUIVO = "historico.csv"
URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

fuso = pytz.timezone("America/Sao_Paulo")

# -------------------------
# GARANTE CSV
# -------------------------
if not os.path.exists(ARQUIVO):
    pd.DataFrame(
        columns=["codigo","nome","objeto","data","link","registro"]
    ).to_csv(ARQUIVO, index=False)

# -------------------------
# EXTRAÇÃO (MONITOR)
# -------------------------
def extrair():
    dados = []

    try:
        r = requests.get(URL, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")

        textos = soup.get_text("\n").split("\n")

        for i in range(len(textos)):
            linha = textos[i].strip()

            if "/" in linha and len(linha) < 20:
                try:
                    codigo = linha
                    nome = textos[i+1].strip()
                    status = textos[i+2].strip()
                    data = textos[i+3].strip()

                    objeto = f"{nome} | {status}".replace(",", " ")

                    dados.append([codigo, nome, objeto, data, URL])
                except:
                    pass
    except Exception as e:
        print("Erro:", e)

    return dados

# -------------------------
# ROTA MONITOR (CRON)
# -------------------------
@app.route("/rodar-monitor")
def rodar_monitor():
    itens = extrair()

    if os.path.exists(ARQUIVO):
        df_existente = pd.read_csv(ARQUIVO)
        existentes = set(df_existente["codigo"].astype(str))
    else:
        existentes = set()

    novos = 0

    for item in itens:
        if item[0] not in existentes:
            agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M")

            nova = pd.DataFrame([item + [agora]],
                columns=["codigo","nome","objeto","data","link","registro"])

            nova.to_csv(ARQUIVO, mode="a", header=False, index=False)

            novos += 1

    return f"{novos} novos registros"

# -------------------------
# API (NOTIFICADOR)
# -------------------------
@app.route("/dados")
def dados():
    try:
        df = pd.read_csv(ARQUIVO)
        return df.to_json(orient="records")
    except:
        return []

# -------------------------
# BOTÃO TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    codigo = f"TESTE{datetime.now().strftime('%H%M%S')}/26"

    nova = pd.DataFrame([[
        codigo,
        "Licitação Teste",
        "Objeto teste automático",
        agora,
        "https://teste.com",
        agora
    ]], columns=["codigo","nome","objeto","data","link","registro"])

    nova.to_csv(ARQUIVO, mode="a", header=False, index=False)

    return redirect("/")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/")
def home():
    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    try:
        df = pd.read_csv(ARQUIVO)
    except:
        df = pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False, na=False)]

    if not df.empty:
        df = df.sort_values(by="registro", ascending=False)

        df["link"] = df["link"].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>'
        )

        tabela = df.to_html(index=False, escape=False)
    else:
        tabela = "<p>Sem dados ainda</p>"

    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>
        <style>
            body {{font-family: Arial; background:#f4f6f9; padding:20px;}}
            .card {{background:white; padding:20px; border-radius:10px;}}
            table {{width:100%; border-collapse:collapse;}}
            th {{background:#0078D4; color:white; padding:10px;}}
            td {{padding:8px; border-bottom:1px solid #ddd;}}
        </style>
    </head>

    <body>
        <div class="card">
            <h2>📊 Monitor EMBASA</h2>

            <form>
                <input name="codigo" placeholder="Código">
                <input name="objeto" placeholder="Objeto">
                <button type="submit">Filtrar</button>
            </form>

            <br>

            <a href="/teste">
                <button>🚀 Testar Notificação</button>
            </a>

            <br><br>

            {tabela}
        </div>
    </body>
    </html>
    """

# -------------------------
# EXECUÇÃO
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)