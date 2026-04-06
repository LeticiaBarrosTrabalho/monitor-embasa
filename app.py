from flask import Flask, request
import pandas as pd
import os
from datetime import datetime
import pytz

app = Flask(__name__)

ARQUIVO = "historico.csv"
fuso = pytz.timezone("America/Sao_Paulo")

# -------------------------
# GARANTE ARQUIVO
# -------------------------
if not os.path.exists(ARQUIVO):
    pd.DataFrame(
        columns=["codigo","nome","objeto","data","link","registro"]
    ).to_csv(ARQUIVO, index=False)

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    try:
        df = pd.read_csv(ARQUIVO)
    except:
        df = pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False, na=False)]

    if not df.empty:
        df = df.sort_values(by="registro", ascending=False)
        df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>')
        tabela = df.to_html(classes="table", index=False, escape=False)
    else:
        tabela = "<p>Sem dados ainda</p>"

    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>
        <style>
            body {{ font-family: Arial; background: #f4f6f9; padding: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #0078D4; color: white; padding: 10px; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            input {{ padding: 8px; margin: 5px; }}
            button {{ padding: 8px 15px; background: #0078D4; color: white; border: none; }}
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

        <a href="/teste"><button>🚀 Testar</button></a>

        <br><br>

        {tabela}
    </div>

    </body>
    </html>
    """

# -------------------------
# API DADOS
# -------------------------
@app.route("/dados")
def dados():
    try:
        df = pd.read_csv(ARQUIVO)
        return df.to_json(orient="records")
    except:
        return "[]"

# -------------------------
# TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    linha = pd.DataFrame([[
        f"TESTE{datetime.now().strftime('%H%M%S')}/26",
        "Licitação Teste",
        "Objeto teste automático",
        agora,
        "https://teste.com",
        agora
    ]], columns=["codigo","nome","objeto","data","link","registro"])

    linha.to_csv(ARQUIVO, mode="a", header=False, index=False)

    return "OK"

# -------------------------
# EXECUÇÃO
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)