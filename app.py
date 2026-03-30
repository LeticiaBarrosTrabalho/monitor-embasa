from flask import Flask
import pandas as pd
import threading
import os
import time
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
            body { font-family: Arial; background:#0f172a; color:white; }
            table { width:100%; border-collapse: collapse; }
            th, td { padding:10px; border:1px solid #334155; }
            th { background:#1e293b; }
            tr:hover { background:#334155; }
        </style>
    </head>
    <body>
        <h1>📊 Dashboard de Licitações</h1>
    """

    html += df.tail(50).to_html(index=False)

    html += "</body></html>"

    return html

# -------------------------
# HEALTH CHECK (IMPORTANTE)
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