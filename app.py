from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)
DB = "historico.db"
fuso = pytz.timezone("America/Sao_Paulo")

# -------------------------
# BANCO DE DADOS
# -------------------------
def conectar():
    return sqlite3.connect(DB)

def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nome TEXT,
        objeto TEXT,
        data TEXT,
        link TEXT,
        registro TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_banco()

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/")
def home():
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM registros ORDER BY id DESC")
    dados = c.fetchall()

    conn.close()

    linhas = ""

    for d in dados:
        linhas += f"""
        <tr>
            <td>{d[1]}</td>
            <td>{d[2]}</td>
            <td>{d[3]}</td>
            <td>{d[4]}</td>
            <td><a href="{d[5]}" target="_blank">🔗 Abrir</a></td>
            <td>{d[6]}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>

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
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            button {{
                background: #0078D4;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
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
        </style>

        <script>
        function testar() {{
            fetch('/teste')
            .then(() => alert('✔ Teste enviado! Verifique o Windows'))
        }}
        </script>

    </head>

    <body>

    <div class="card">
        <h2>📊 Monitor EMBASA</h2>

        <button onclick="testar()">🔔 Testar Notificação</button>

        <br><br>

        <table>
            <tr>
                <th>Código</th>
                <th>Nome</th>
                <th>Objeto</th>
                <th>Data</th>
                <th>Link</th>
                <th>Registrado em</th>
            </tr>

            {linhas}
        </table>

    </div>

    </body>
    </html>
    """

# -------------------------
# API DADOS
# -------------------------
@app.route("/dados")
def dados():
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT * FROM registros ORDER BY id DESC")
    dados = c.fetchall()

    conn.close()

    lista = []
    for d in dados:
        lista.append({
            "codigo": d[1],
            "nome": d[2],
            "objeto": d[3],
            "data": d[4],
            "link": d[5],
            "registro": d[6]
        })

    return jsonify(lista)

# -------------------------
# NOVO REGISTRO
# -------------------------
@app.route("/novo", methods=["POST"])
def novo():
    dados = request.json

    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    INSERT INTO registros (codigo, nome, objeto, data, link, registro)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dados["codigo"],
        dados["nome"],
        dados["objeto"],
        dados["data"],
        dados["link"],
        agora
    ))

    conn.commit()
    conn.close()

    return "OK"

# -------------------------
# TESTE
# -------------------------
@app.route("/teste")
def teste():
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    INSERT INTO registros (codigo, nome, objeto, data, link, registro)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        f"TESTE {hash(agora)}",
        "Teste manual",
        "Teste de notificação",
        agora,
        "https://teste.com",
        agora
    ))

    conn.commit()
    conn.close()

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)