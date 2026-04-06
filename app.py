from flask import Flask, render_template, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

fuso = pytz.timezone("America/Sao_Paulo")

registros = []

def add_log(texto):
    registros.insert(0, {
        "texto": texto,
        "hora": datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
    })

@app.route("/")
def index():
    return render_template("index.html", registros=registros)

# botão de teste
@app.route("/teste")
def teste():
    add_log("🔔 TESTE MANUAL DE NOTIFICAÇÃO")
    return jsonify({"status": "ok"})

# endpoint usado pelo monitor
@app.route("/evento/<msg>")
def evento(msg):
    add_log(f"📡 {msg}")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)