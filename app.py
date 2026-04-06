from flask import Flask, jsonify
import pandas as pd
from database import conectar, criar_tabela

app = Flask(__name__)
criar_tabela()

# -------------------------
# CARREGAR DADOS
# -------------------------
def carregar():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM licitacoes", conn)
    conn.close()
    return df

# -------------------------
# HOME (DASHBOARD)
# -------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Dashboard EMBASA</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial; background:#f4f6f9; padding:20px; }
            .card { background:white; padding:20px; border-radius:10px; margin-bottom:20px; }
            .table { width:100%; border-collapse:collapse; }
            .table th { background:#0078D4; color:white; padding:10px; }
            .table td { padding:8px; border-bottom:1px solid #ddd; }
            button { padding:10px; background:#0078D4; color:white; border:none; border-radius:5px; cursor:pointer; }
        </style>
    </head>

    <body>
    <h2>📊 Monitor EMBASA</h2>

    <button onclick="teste()">🚀 Testar Notificação</button>

    <br><br>

    <canvas id="grafico"></canvas>

    <br><br>

    <table class="table" id="tabela"></table>

    <script>
    function teste(){
        fetch('/teste')
    }

    function atualizar(){
        fetch('/dados')
        .then(r=>r.json())
        .then(data=>{
            let html = "<tr><th>Código</th><th>Nome</th><th>Objeto</th><th>Data</th><th>Link</th></tr>";

            data.slice().reverse().forEach(d=>{
                html += `<tr>
                    <td>${d.codigo}</td>
                    <td>${d.nome}</td>
                    <td>${d.objeto}</td>
                    <td>${d.data}</td>
                    <td><a href="${d.link}" target="_blank">Abrir</a></td>
                </tr>`;
            });

            document.getElementById("tabela").innerHTML = html;

            // gráfico
            const agrupado = {};
            data.forEach(d=>{
                const dia = d.registro.split(" ")[0];
                agrupado[dia] = (agrupado[dia] || 0) + 1;
            });

            const labels = Object.keys(agrupado);
            const valores = Object.values(agrupado);

            new Chart(document.getElementById('grafico'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Registros por dia',
                        data: valores
                    }]
                }
            });
        });
    }

    setInterval(atualizar, 10000);
    atualizar();
    </script>

    </body>
    </html>
    """

# -------------------------
# API
# -------------------------
@app.route("/dados")
def dados():
    df = carregar()
    return df.to_json(orient="records")

# -------------------------
# TESTE
# -------------------------
@app.route("/teste")
def teste():
    from datetime import datetime
    import pytz

    fuso = pytz.timezone("America/Sao_Paulo")

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

    return jsonify({"status":"ok"})

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)