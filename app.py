from flask import Flask, request
import pandas as pd
from database import conectar, criar_tabela

app = Flask(__name__)
criar_tabela()

def carregar():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM licitacoes", conn)
    conn.close()
    return df

@app.route("/")
def home():
    df = carregar()

    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    if codigo:
        df = df[df["codigo"].str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].str.contains(objeto, case=False, na=False)]

    # KPIs
    total = len(df)

    try:
        df["registro_dt"] = pd.to_datetime(df["registro"], errors="coerce")
        hoje = pd.Timestamp.today().date()
        novos_hoje = len(df[df["registro_dt"].dt.date == hoje])

        grafico = df.groupby(df["registro_dt"].dt.date).size()
        labels = list(grafico.index.astype(str))
        valores = list(grafico.values)
    except:
        novos_hoje = 0
        labels, valores = [], []

    # tabela
    if not df.empty:
        df = df.sort_values(by="id", ascending=False)
        df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">Abrir</a>')
        tabela = df.to_html(index=False, escape=False, classes="table")
    else:
        tabela = "<p>Sem dados</p>"

    return f"""
    <html>
    <head>
        <title>Dashboard EMBASA</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: Arial;
                background: #f4f6f9;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: auto;
            }}

            .cards {{
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }}

            .card {{
                flex: 1;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }}

            .card h2 {{
                margin: 0;
                font-size: 30px;
                color: #0078D4;
            }}

            .card p {{
                margin: 5px;
                color: #666;
            }}

            .filtros {{
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
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

            .table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            .table th {{
                background: #0078D4;
                color: white;
                padding: 10px;
            }}

            .table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
        </style>
    </head>

    <body>
    <div class="container">

        <h2>📊 Dashboard EMBASA</h2>

        <div class="cards">
            <div class="card">
                <h2>{total}</h2>
                <p>Total de Registros</p>
            </div>

            <div class="card">
                <h2>{novos_hoje}</h2>
                <p>Novos Hoje</p>
            </div>
        </div>

        <div class="filtros">
            <form>
                <input name="codigo" placeholder="Código">
                <input name="objeto" placeholder="Objeto">
                <button>Filtrar</button>
                <a href="/teste"><button type="button">🚀 Teste</button></a>
            </form>
        </div>

        <canvas id="grafico"></canvas>

        <script>
        new Chart(document.getElementById('grafico'), {{
            type: 'line',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Registros por dia',
                    data: {valores},
                    tension: 0.3
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

@app.route("/dados")
def dados():
    df = carregar()
    return df.to_json(orient="records")

@app.route("/teste")
def teste():
    from datetime import datetime
    import pytz
    fuso = pytz.timezone("America/Sao_Paulo")

    from database import conectar
    conn = conectar()
    cursor = conn.cursor()

    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
    INSERT INTO licitacoes (codigo, nome, objeto, data, link, registro)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        f"TESTE{datetime.now().strftime('%H%M%S')}",
        "Teste",
        "Objeto teste",
        agora,
        "https://teste.com",
        agora
    ))

    conn.commit()
    conn.close()

    return "OK"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)