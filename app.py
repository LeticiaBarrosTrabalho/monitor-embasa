from flask import Flask, request, redirect
import pandas as pd
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Fuso horário Brasil
fuso = pytz.timezone("America/Sao_Paulo")

ARQUIVO = "historico.csv"

# -------------------------
# GARANTE ARQUIVO EXISTENTE
# -------------------------
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        f.write("codigo,nome,objeto,data,link,registro\n")

# -------------------------
# HOME (DASHBOARD)
# -------------------------
@app.route("/")
def home():
    filtro_codigo = request.args.get("codigo", "").lower()
    filtro_objeto = request.args.get("objeto", "").lower()

    try:
        df = pd.read_csv(ARQUIVO)
    except:
        df = pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

    # 🔍 FILTROS
    if filtro_codigo:
        df = df[df["codigo"].astype(str).str.lower().str.contains(filtro_codigo)]

    if filtro_objeto:
        df = df[df["objeto"].astype(str).str.lower().str.contains(filtro_objeto)]

    # 🔗 LINK CLICÁVEL
    if not df.empty:
        df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">Abrir</a>')

    html = f"""
    <html>
    <head>
        <title>Monitor de Licitações</title>
    </head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>📊 Monitor de Licitações</h2>

        <form method="get">
            <input type="text" name="codigo" placeholder="Filtrar por código">
            <input type="text" name="objeto" placeholder="Filtrar por objeto">
            <button type="submit">Filtrar</button>
        </form>

        <br>

        <a href="/teste">
            <button>🚀 Testar Notificação</button>
        </a>

        <br><br>
    """

    if df.empty:
        html += "<p>Sem dados ainda</p>"
    else:
        html += df.tail(50).to_html(index=False, escape=False)

    html += "</body></html>"

    return html

# -------------------------
# BOTÃO TESTE (FINAL CORRIGIDO)
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    # 🔥 GARANTE QUE CADA TESTE É ÚNICO
    unique_id = datetime.now().strftime("%H%M%S%f")

    linha = [
        f"TESTE{unique_id}/26",
        "Licitação Teste",
        f"Objeto de teste {unique_id}",
        agora,
        "https://teste.com",
        agora
    ]

    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        f.write(",".join(linha) + "\n")

    return redirect("/")

# -------------------------
# EXECUÇÃO
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)