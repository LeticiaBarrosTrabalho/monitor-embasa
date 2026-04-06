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
def garantir_arquivo():
    if not os.path.exists(ARQUIVO):
        pd.DataFrame(
            columns=["codigo","nome","objeto","data","link","registro"]
        ).to_csv(ARQUIVO, index=False)

# -------------------------
# LEITURA SEGURA
# -------------------------
def ler_csv_seguro():
    try:
        return pd.read_csv(ARQUIVO)
    except:
        return pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    garantir_arquivo()
    df = ler_csv_seguro()

    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False, na=False)]

    # gráfico
    try:
        df["registro_dt"] = pd.to_datetime(df["registro"], errors="coerce")
        grafico = df.groupby(df["registro_dt"].dt.date).size()
        labels = list(grafico.index.astype(str))
        valores = list(grafico.values)
    except:
        labels, valores = [], []

    # tabela
    if not df.empty:
        df = df.sort_values(by="registro", ascending=False)
        df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>')
        tabela = df.to_html(index=False, escape=False)
    else:
        tabela = "<p>Sem dados</p>"

    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body style="font-family: Arial; padding:20px; background:#f4f6f9;">

    <h2>📊 Monitor EMBASA</h2>

    <form>
        <input name="codigo" placeholder="Código">
        <input name="objeto" placeholder="Objeto">
        <button>Filtrar</button>
    </form>

    <br>
    <a href="/teste"><button>🚀 Testar</button></a>

    <br><br>

    <canvas id="grafico"></canvas>

    <script>
    new Chart(document.getElementById('grafico'), {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [{{
                label: 'Registros por dia',
                data: {valores}
            }}]
        }}
    }});
    </script>

    <br><br>
    {tabela}

    </body>
    </html>
    """

# -------------------------
# API
# -------------------------
@app.route("/dados")
def dados():
    garantir_arquivo()
    df = ler_csv_seguro()
    return df.to_json(orient="records")

# -------------------------
# TESTE
# -------------------------
@app.route("/teste")
def teste():
    garantir_arquivo()

    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    linha = pd.DataFrame([[
        f"TESTE{datetime.now().strftime('%H%M%S')}",
        "Teste",
        "Objeto teste",
        agora,
        "https://teste.com",
        agora
    ]], columns=["codigo","nome","objeto","data","link","registro"])

    try:
        linha.to_csv(ARQUIVO, mode="a", header=False, index=False)
    except:
        pass

    return "OK"

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)