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
    df = pd.read_sql_query("SELECT * FROM licitacoes ORDER BY id DESC", conn)
    conn.close()
    return df

# -------------------------
# HOME (SOMENTE REGISTROS)
# -------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Monitor EMBASA</title>
        <style>
            body { font-family: Arial; background:#f4f6f9; padding:20px; }
            .container { max-width:1000px; margin:auto; }

            h2 { color:#0078D4; }

            button {
                padding:10px;
                background:#0078D4;
                color:white;
                border:none;
                border-radius:5px;
                cursor:pointer;
            }

            table {
                width:100%;
                border-collapse:collapse;
                background:white;
                margin-top:20px;
            }

            th {
                background:#0078D4;
                color:white;
                padding:10px;
                text-align:left;
            }

            td {
                padding:8px;
                border-bottom:1px solid #ddd;
            }

            .novo {
                background:#e8fff0;
            }
        </style>
    </head>

    <body>
    <div class="container">

        <h2>📡 Monitor de Licitações</h2>

        <button onclick="teste()">🚀 Teste de Notificação</button>

        <table id="tabela"></table>

    </div>

    <script>

    let ultimoId = 0;

    function teste(){
        fetch('/teste')
    }

    function atualizar(){
        fetch('/dados')
        .then(r=>r.json())
        .then(data=>{

            let html = `
            <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Objeto</th>
                <th>Data</th>
                <th>Link</th>
            </tr>`;

            data.forEach(d => {

                let classe = d.id > ultimoId ? "novo" : "";

                html += `
                <tr class="${classe}">
                    <td>${d.codigo}</td>
                    <td>${d.nome}</td>
                    <td>${d.objeto}</td>
                    <td>${d.data}</td>
                    <td><a href="${d.link}" target="_blank">Abrir</a></td>
                </tr>`;
            });

            if(data.length > 0){
                ultimoId = Math.max(...data.map(d=>d.id));
            }

            document.getElementById("tabela").innerHTML = html;

        });
    }

    setInterval(atualizar, 5000);
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