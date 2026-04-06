from flask import Flask, jsonify
from flask_socketio import SocketIO
import pandas as pd
from database import conectar, criar_tabela
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
# MONITOR TEMPO REAL
# -------------------------
def monitor_socket():
    ultimo_total = 0

    while True:
        try:
            df = carregar()
            total = len(df)

            if total != ultimo_total:
                socketio.emit("atualizar", df.to_dict(orient="records"))
                print("📡 Atualização enviada via WebSocket")

                ultimo_total = total

        except Exception as e:
            print("Erro socket:", e)

        time.sleep(3)

# thread em background
threading.Thread(target=monitor_socket, daemon=True).start()

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Dashboard EMBASA PRO</title>
        <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>

    <body style="font-family:Arial; padding:20px; background:#f4f6f9">

    <h2>📊 Dashboard EMBASA (Tempo Real PRO)</h2>

    <h3>Total: <span id="total">0</span></h3>

    <button onclick="rodarTeste()">🚀 Teste</button>

    <br><br>
    <canvas id="grafico"></canvas>

    <br><br>
    <table border="1" id="tabela"></table>

    <script>
    const socket = io();

    let grafico;

    socket.on("atualizar", function(data){
        console.log("Atualizado!");

        document.getElementById("total").innerText = data.length;

        // tabela
        let html = "<tr><th>Código</th><th>Nome</th><th>Objeto</th><th>Data</th></tr>";
        data.slice().reverse().forEach(d=>{
            html += `<tr>
                <td>${d.codigo}</td>
                <td>${d.nome}</td>
                <td>${d.objeto}</td>
                <td>${d.data}</td>
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
                        data: valores
                    }]
                }
            });
        }

        // alerta
        alert("🚨 Nova licitação detectada!");
    });

    function rodarTeste(){
        fetch('/teste');
    }
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

    return jsonify({"ok": True})

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)