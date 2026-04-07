from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import os
from datetime import datetime
import pytz

app = Flask(__name__)

ARQUIVO = "historico.csv"
fuso = pytz.timezone("America/Sao_Paulo")

# cria arquivo se não existir
if not os.path.exists(ARQUIVO):
    pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"]).to_csv(ARQUIVO, index=False)

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/")
def home():
    df = pd.read_csv(ARQUIVO)

    # ordena
    df = df.sort_values(by="registro", ascending=False)

    # link clicável
    df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>')

    tabela = df.to_html(index=False, escape=False)

    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>

        <style>
            body {{
                font-family: Arial;
                background: #f4f6f9;
                padding: 20px;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            h2 {{
                margin-bottom: 10px;
            }}

            button {{
                background: #0078D4;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                background: #0078D4;
                color: white;
                padding: 10px;
            }}

            td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
        </style>

        <script>
        function testar() {{
            fetch('/teste')
            .then(() => alert('Teste registrado! Verifique a notificação no Windows'))
        }}
        </script>

    </head>

    <body>

    <div class="card">
        <h2>📊 Monitor EMBASA (Estilo Power BI)</h2>

        <button onclick="testar()">🔔 Testar Notificação</button>

        <br><br>

        {tabela}
    </div>

    </body>
    </html>
    """

# -------------------------
# API PARA MONITOR
# -------------------------
@app.route("/dados")
def dados():
    df = pd.read_csv(ARQUIVO)
    return df.to_json(orient="records")

# -------------------------
# REGISTRAR ALTERAÇÃO
# -------------------------
@app.route("/novo", methods=["POST"])
def novo():
    dados = request.json

    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    linha = [
        dados["codigo"],
        dados["nome"],
        dados["objeto"],
        dados["data"],
        dados["link"],
        agora
    ]

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        f.write(",".join(linha) + "\n")

    return "OK"

# -------------------------
# BOTÃO TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    with open(ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"TESTE,Teste,Teste manual,{agora},https://teste.com,{agora}\n")

    return "OK"

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)