from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)

ARQUIVO = "historico.csv"

# Garante arquivo
if not os.path.exists(ARQUIVO):
    pd.DataFrame(columns=["codigo","nome","objeto","data","link","registro"]).to_csv(ARQUIVO, index=False)

@app.route("/dados")
def dados():
    df = pd.read_csv("historico.csv")
    return df.to_json(orient="records")

    df = pd.read_csv(ARQUIVO)

    if codigo:
        df = df[df["codigo"].astype(str).str.contains(codigo, case=False)]

    if objeto:
        df = df[df["objeto"].astype(str).str.contains(objeto, case=False)]

    df = df.sort_values(by="registro", ascending=False)

    df["link"] = df["link"].apply(lambda x: f'<a href="{x}" target="_blank">🔗 Abrir</a>')

    tabela = df.to_html(classes="table", index=False, escape=False)

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
            .table {{
                width: 100%;
                border-collapse: collapse;
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

        <form>
            <input name="codigo" placeholder="Código">
            <input name="objeto" placeholder="Objeto">
            <button type="submit">Filtrar</button>
        </form>

        <br>

        {tabela}
    </div>

    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)