from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)

ARQUIVO = "historico.csv"

# -------------------------
# GARANTE ARQUIVO
# -------------------------
if not os.path.exists(ARQUIVO):
    pd.DataFrame(
        columns=["codigo","nome","objeto","data","link","registro"]
    ).to_csv(ARQUIVO, index=False)

# -------------------------
# API (USADA PELO NOTIFICADOR)
# -------------------------
@app.route("/dados")
def dados():
    try:
        df = pd.read_csv(ARQUIVO)
        return df.to_json(orient="records")
    except:
        return []

# -------------------------
# DASHBOARD (ROTA PRINCIPAL)
# -------------------------
@app.route("/")
def home():
    codigo = request.args.get("codigo", "")
    objeto = request.args.get("objeto", "")

    try:
        df = pd.read_csv(ARQUIVO)
    except:
        df = pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"])

    # FILTROS
    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False, na=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False, na=False)]

    # ORDENAÇÃO
    if not df.empty:
        df = df.sort_values(by="registro", ascending=False)

        # LINK CLICÁVEL
        df["link"] = df["link"].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>'
        )

        tabela = df.to_html(index=False, escape=False)
    else:
        tabela = "<p>Sem dados ainda</p>"

    # HTML ESTILO POWER BI
    return f"""
    <html>
    <head>
        <title>Monitor EMBASA</title>
        <style>
            body {{
                font-family: Arial;
                background-color: #f4f6f9;
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
                text-align: left;
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
            <h2>📊 Monitor EMBASA (Estilo Power BI)</h2>

            <form method="get">
                <input name="codigo" placeholder="Filtrar código" value="{codigo}">
                <input name="objeto" placeholder="Filtrar objeto" value="{objeto}">
                <button type="submit">Filtrar</button>
            </form>

            <br>

            {tabela}
        </div>
    </body>
    </html>
    """

# -------------------------
# EXECUÇÃO (RENDER)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)