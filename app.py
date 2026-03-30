from flask import Flask, redirect
import threading
import os
import time
from datetime import datetime

from monitor import monitor

app = Flask(__name__)

ARQUIVO_LOG = "historico.txt"

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def home():
    try:
        with open(ARQUIVO_LOG, encoding="utf-8") as f:
            linhas = f.readlines()[-50:]
    except:
        linhas = []

    html = """
    <html>
    <head>
        <title>Dashboard Licitações</title>
        <style>
            body {
                font-family: Arial;
                background: #0f172a;
                color: white;
                padding: 20px;
                text-align: center;
            }
            .card {
                background: #1e293b;
                padding: 15px;
                margin: 10px auto;
                border-radius: 10px;
                max-width: 800px;
            }
            button {
                background: #22c55e;
                border: none;
                padding: 15px 25px;
                color: white;
                font-size: 16px;
                border-radius: 10px;
                cursor: pointer;
                margin-bottom: 20px;
            }
            button:hover {
                background: #16a34a;
            }
        </style>
    </head>
    <body>
        <h1>📊 Monitor de Licitações</h1>

        <form action="/teste">
            <button type="submit">🚀 Simular Nova Licitação</button>
        </form>
    """

    for linha in reversed(linhas):
        html += f'<div class="card">{linha}</div>'

    html += "</body></html>"
    return html

# -------------------------
# BOTÃO DE TESTE
# -------------------------

@app.route("/teste")
def teste():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    linha_teste = f"TESTE999/26 | Licitação Teste | https://teste.com | {agora}"

    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(linha_teste + "\n")

    print("🧪 Teste gerado:", linha_teste)

    return redirect("/")

# -------------------------
# MONITOR EM BACKGROUND
# -------------------------

def iniciar_monitor():
    time.sleep(10)
    monitor()

thread = threading.Thread(target=iniciar_monitor)
thread.daemon = True
thread.start()

# -------------------------
# START
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)