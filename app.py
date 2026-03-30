from flask import Flask
import threading
import os
import time

from monitor import monitor

app = Flask(__name__)

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def home():
    try:
        with open("historico.txt", encoding="utf-8") as f:
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
            }
            .card {
                background: #1e293b;
                padding: 15px;
                margin: 10px;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <h1>📊 Monitor de Licitações</h1>
    """

    for linha in reversed(linhas):
        html += f'<div class="card">{linha}</div>'

    html += "</body></html>"
    return html

# -------------------------
# MONITOR EM BACKGROUND (COM DELAY)
# -------------------------

def iniciar_monitor():
    time.sleep(10)  # ⬅️ MUITO IMPORTANTE (deixa o servidor subir primeiro)
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