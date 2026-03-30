from flask import Flask, redirect
import pandas as pd
import threading
import os
import time
from datetime import datetime
from monitor import monitor

app = Flask(__name__)

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/")
def dashboard():
    if not os.path.exists("historico.csv"):
        return "Sem dados ainda"

    df = pd.read_csv("historico.csv")

    html = """
    <html>
    <head>
        <title>Dashboard Licitações</title>
        <style>
            body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
            table { width:90%; margin:auto; border-collapse: collapse; }
            th, td { padding:10px; border:1px solid #334155; }
            th { background:#1e293b; }
            tr:hover { background:#334155; }
            button { 
                background:#22c55e; 
                padding:12px; 
                border:none; 
                color:white; 
                border-radius:8px; 
                cursor:pointer; 
                margin:15px;
            }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard de Licitações</h1>

        <form action="/teste">
            <button>🚀 Testar Notificação</button>
        </form>
    """

    html += df.tail(50).to_html(index=False)

    html += "</body></html>"

    return html

# -------------------------
# BOTÃO DE TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    linha = [
        "TESTE999/26",
        "Licitação Teste",
        "Objeto completo de teste manual",
        agora,
        "https://teste.com",
        agora
    ]

    existe = os.path.exists("historico.csv")

    with open("historico.csv", "a", encoding="utf-8") as f:
        if not existe:
            f.write("codigo,nome,objeto,data,link,registro\n")

        f.write(",".join(linha) + "\n")

    return redirect("/")

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/health")
def health():
    return "ok", 200

# -------------------------
# MONITOR EM THREAD
# -------------------------
def iniciar_monitor():
    time.sleep(10)
    monitor()

thread = threading.Thread(target=iniciar_monitor, daemon=True)
thread.start()

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)