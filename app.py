from flask import Flask, request, redirect
import pandas as pd
import threading
import os
import time
from datetime import datetime
from monitor import monitor

app = Flask(__name__)

# -------------------------
# DASHBOARD COM FILTROS
# -------------------------
@app.route("/")
def dashboard():
    if not os.path.exists("historico.csv"):
        return "Sem dados ainda"

    df = pd.read_csv("historico.csv")

    # -------------------------
    # PEGAR FILTROS DA URL
    # -------------------------
    tipo = request.args.get("tipo", "")
    busca = request.args.get("busca", "")

    # -------------------------
    # APLICAR FILTROS
    # -------------------------
    if tipo:
        df = df[df["objeto"].str.contains(tipo, case=False, na=False)]

    if busca:
        df = df[df["objeto"].str.contains(busca, case=False, na=False)]

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
            input, select {
                padding:10px;
                margin:5px;
                border-radius:6px;
                border:none;
            }
            button { 
                background:#22c55e; 
                padding:10px; 
                border:none; 
                color:white; 
                border-radius:8px; 
                cursor:pointer; 
            }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard de Licitações</h1>

        <form method="get">
            <select name="tipo">
                <option value="">Todos</option>
                <option value="licitação">Licitação</option>
                <option value="pregão">Pregão</option>
                <option value="edital">Edital</option>
            </select>

            <input type="text" name="busca" placeholder="Buscar no objeto...">

            <button type="submit">Filtrar</button>
        </form>

        <br>

        <form action="/teste">
            <button>🚀 Testar Notificação</button>
        </form>
    """

    html += df.tail(50).to_html(index=False)

    html += "</body></html>"

    return html

# -------------------------
# BOTÃO TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    linha = [
        "TESTE999/26",
        "Licitação Teste",
        "Objeto de teste com filtro edital",
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
# MONITOR THREAD
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