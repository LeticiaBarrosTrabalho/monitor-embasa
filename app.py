from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
import pytz

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

fuso = pytz.timezone("America/Sao_Paulo")

# memória dos registros
registros = []

@app.route("/")
def index():
    return render_template("index.html", registros=registros)

# 🔥 função que recebe evento do monitor
def novo_registro(dado):
    agora = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")

    registro = {
        "texto": dado,
        "hora": agora
    }

    registros.insert(0, registro)

    # envia em tempo real para frontend
    socketio.emit("nova_notificacao", registro)

    return registro


# TESTE MANUAL
@app.route("/teste")
def teste():
    novo_registro("🔔 TESTE DE ALTERAÇÃO DETECTADO")
    return "OK"

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)