from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime
import pytz

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

fuso = pytz.timezone("America/Sao_Paulo")

registros = []

def novo_registro(texto):
    registro = {
        "texto": texto,
        "hora": datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
    }

    registros.insert(0, registro)

    socketio.emit("nova_notificacao", registro)
    return registro


@app.route("/")
def index():
    return render_template("index.html", registros=registros)


# 🔥 BOTÃO DE TESTE (Windows + Browser)
@app.route("/teste-notificacao")
def teste_notificacao():
    novo_registro("🔔 TESTE DE NOTIFICAÇÃO WINDOWS / SISTEMA")
    return "OK"


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)