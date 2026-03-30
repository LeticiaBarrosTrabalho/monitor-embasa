from flask import Flask
import threading
import os

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
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
            }
            .card {
                background: #1e293b;
                padding: 15px;
                margin: 10px auto;
                border-radius: 10px;
                max-width: 800px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
            }
        </style>
    </head>
    <body>
        <h1>📊 Monitor de Licitações</h1>
    """

    for linha in reversed(linhas):
        html += f'<div class="card">{linha}</div>'

    html += """
    </body>
    </html>
    """

    return html

# -------------------------
# MONITOR EM BACKGROUND
# -------------------------

def iniciar_monitor():
    monitor()

# Thread em modo daemon (IMPORTANTE pro Render)
threading.Thread(target=iniciar_monitor, daemon=True).start()

# -------------------------
# START DO SERVIDOR
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ESSENCIAL PRO RENDER
    app.run(host="0.0.0.0", port=port)