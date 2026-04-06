from flask import Flask, jsonify, request
from datetime import datetime
import pytz

app = Flask(__name__)

fuso = pytz.timezone("America/Sao_Paulo")

estado = {
    "versao": 0,
    "ultima_mudanca": None
}

@app.route("/status")
def status():
    return jsonify(estado)

@app.route("/alterar", methods=["POST"])
def alterar():
    global estado
    estado["versao"] += 1
    estado["ultima_mudanca"] = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
    return jsonify(estado)

@app.route("/")
def home():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)