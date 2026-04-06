from flask import Flask, request, jsonify
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
# HOME
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
            .container { max-width:1200px; margin:auto; }

            .cards { display:flex; gap:20px; margin-bottom:20px; }
            .card {
                flex:1;
                background:white;
                padding:20px;
                border-radius:10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.1);
                text-align:center;
            }

            .card h2 { color:#0078D4; margin:0; }

            .table {
                width:100%;
                border-collapse: collapse;
                background:white;
            }

            .table th {
                background:#0078D4;
                color:white;
                padding:10px;
            }

            .table td {
                padding:8px;
                border-bottom:1px solid #ddd;
            }

            button {
                padding:10px;
                background:#0078D4;
                color:white;
                border:none;
                border-radius:5px;
                cursor:pointer;
            }
        </style>
    </head>

    <body>
    <div class="container">

        <h2>📊 Dashboard EMBASA (Tempo Real)</h2>

        <div class="cards">
            <div class="card">
                <h2 id="total">0</h2>
                <p>Total</p>
            </div>
            <div class="card">
                <h2 id="hoje">0</h2>
                <p>Hoje</p>
            </div>
        </div>

        <button onclick="rodarTeste()">🚀 Testar</button>

        <br><br>

        <canvas id="grafico"></canvas>

        <br><br>

        <table class="table" id="tabela"></table>

    </div>

    <script>
    let grafico;

    function rodarTeste(){
        fetch('/teste')
        .then(() => mostrarAlerta("Teste enviado"))
    }

    function mostrarAlerta(msg){
        const div = document.createElement("div");
        div.innerHTML = msg;
        div.style.position="fixed";
        div.style.top="20px";
        div.style.right="20px";
        div.style.background="green";
        div.style.color="white";
        div.style.padding="15px";
        div.style.borderRadius="8px";
        document.body.appendChild(div);

        setTimeout(()=>div.remove(),2000);
    }

    function atualizar(){
        fetch('/dados')
        .then(r=>r.json())
        .then(data=>{
            document.getElementById("total").innerText = data.length;

            const hoje = new Date().toISOString().slice(0,10);
            const novos = data.filter(x => x.registro?.includes(hoje)).length;
            document.getElementById("hoje").innerText = novos;

            // tabela
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
                const dia = d.registro?.split(" ")[0];
                agrupado[dia] = (agrupado[dia] || 0) + 1;
            });

            const labels = Object.keys(agrupado);
            const valores = Object.values(agrupado);

            if(grafico){
                grafico.data.labels = labels;
                grafico.data.datasets[0].data = valores;
                grafico.update();
            } else {
                grafico = new Chart(document.getElementById('grafico'), {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Registros por dia',
                            data: valores,
                            tension: 0.3
                        }]
                    }
                });
            }

            // alerta de novo registro
            if(window.ultimoTotal !== undefined && data.length > window.ultimoTotal){
                mostrarAlerta("🚨 Nova licitação detectada!");
            }

            window.ultimoTotal = data.length;
        });
    }

    setInterval(atualizar, 5000); // 🔥 tempo real
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

    return jsonify({"status": "ok"})

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)