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

    df = df.sort_values(by="id", ascending=False)

    df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>')

    tabela = df.to_html(index=False, escape=False)

    return f"""
    <html>
    <body style="font-family: Arial; padding:20px;">
    <h2>📊 Monitor EMBASA</h2>

    <form>
        <input name="codigo" placeholder="Código">
        <input name="objeto" placeholder="Objeto">
        <button>Filtrar</button>
    </form>

    <br>
    <a href="/teste"><button>🚀 Teste</button></a>

    <br><br>
    {tabela}
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