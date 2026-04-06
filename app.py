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
# HOME (DASHBOARD)
# -------------------------
@app.route("/")
def home():
    try:
        df = pd.read_csv(ARQUIVO)
    except:
        df = pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

    # 🔍 FILTROS
    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False, na=False)]

    # 📊 GRÁFICO
    try:
        df["registro_dt"] = pd.to_datetime(df["registro"], errors="coerce")
        grafico = df.groupby(df["registro_dt"].dt.date).size()

        labels = list(grafico.index.astype(str))
        valores = list(grafico.values)
    except:
        labels = []
        valores = []

    # 🔗 LINK CLICÁVEL
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

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

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
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

            input {{
                padding: 8px;
                margin: 5px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }}

            button {{
                padding: 8px 15px;
                background: #0078D4;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
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

        <!-- 📈 GRÁFICO -->
        <canvas id="grafico" height="100"></canvas>

        <script>
        const ctx = document.getElementById('grafico');

        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Licitações por dia',
                    data: {valores},
                    borderWidth: 2
                }}]
            }}
        }});
        </script>

        <br><br>

        {tabela}
    </div>

    </body>
    </html>
    """

# -------------------------
# API (USADA PELO NOTIFICADOR)
# -------------------------
@app.route("/dados")
def dados():
    try:
        df = pd.read_csv(ARQUIVO)
        return df.to_json(orient="records")
    except:
        return "[]"

# -------------------------
# TESTE (GERA NOVO REGISTRO)
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
# EXECUÇÃO (IMPORTANTE PARA RENDER)
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)