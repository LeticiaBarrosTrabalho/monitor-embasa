<<<<<<< HEAD
from flask import Flask, render_template_string
import threading
import time
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO_LOG = "historico.txt"
ARQUIVO_ESTADO = "estado.txt"

PALAVRAS = ["sapiranga", "dragagem", "ete"]

# -------------------------
# UTIL
# -------------------------

def salvar_log(msg):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def salvar_estado(itens):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        f.write("\n".join(itens))

# -------------------------
# EXTRAIR OBJETO
# -------------------------

def extrair_objeto(pagina):
    linhas = pagina.split("\n")

    for i, linha in enumerate(linhas):
        if any(p in linha for p in ["objeto", "descrição", "referente", "finalidade"]):
            return " ".join(linhas[i:i+2])[:300]

    return ""

# -------------------------
# MONITOR
# -------------------------

def monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print("🔎 Monitor rodando...")

    while True:
        try:
            driver.get(URL)
            time.sleep(5)

            texto = driver.find_element("tag name", "body").text.lower()
            linhas = [l.strip() for l in texto.split("\n") if l.strip()]

            registros = []

            # EXTRAÇÃO DOS BLOCOS
            for i in range(len(linhas)):
                linha = linhas[i]

                if "/" in linha and any(c.isdigit() for c in linha):
                    codigo = linha
                    tipo = linhas[i+1] if i+1 < len(linhas) else ""
                    status = linhas[i+2] if i+2 < len(linhas) else ""
                    data_str = linhas[i+3] if i+3 < len(linhas) else ""

                    try:
                        data = datetime.strptime(data_str, "%d/%m/%Y")
                    except:
                        continue

                    registros.append({
                        "codigo": codigo,
                        "tipo": tipo,
                        "status": status,
                        "data": data,
                        "data_str": data_str
                    })

            # ORDENAÇÃO REAL
            registros.sort(key=lambda x: x["data"], reverse=True)

            # LIMITA A 10 MAIS RECENTES
            registros = registros[:10]

            itens_atuais = set()

            elementos = driver.find_elements("tag name", "a")

            for r in registros:
                codigo = r["codigo"]
                data_str = r["data_str"]

                link = ""

                # ASSOCIA LINK
                for el in elementos:
                    if codigo in el.text.lower():
                        link = el.get_attribute("href")
                        break

                objeto = ""

                # ABRE LINK PARA PEGAR OBJETO
                if link:
                    try:
                        driver.execute_script("window.open(arguments[0]);", link)
                        driver.switch_to.window(driver.window_handles[1])

                        time.sleep(3)

                        pagina = driver.find_element("tag name", "body").text.lower()
                        objeto = extrair_objeto(pagina)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except Exception as e:
                        print("Erro ao abrir link:", e)

                item = f"{codigo} | {data_str} | {objeto} | {link}"
                itens_atuais.add(item.lower())

            # COMPARAÇÃO
            itens_antigos = carregar_estado()
            novos = itens_atuais - itens_antigos

            if novos:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                for item in novos:
                    if any(p in item for p in PALAVRAS):
                        msg = f"{item} | {agora}"
                        print("🚨 Nova licitação:", msg)
                        salvar_log(msg)

                salvar_estado(itens_atuais)

        except Exception as e:
            print("Erro geral:", e)

        time.sleep(600)  # 10 minutos

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def home():
    dados = []

    try:
        with open(ARQUIVO_LOG, encoding="utf-8") as f:
            linhas = f.readlines()

        for linha in linhas:
            partes = linha.split("|")

            if len(partes) >= 5:
                dados.append({
                    "codigo": partes[0].strip(),
                    "data": partes[1].strip(),
                    "objeto": partes[2].strip(),
                    "link": partes[3].strip(),
                    "hora": partes[4].strip()
                })

    except:
        pass

    total = len(dados)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Dashboard Licitações</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
    body { background-color: #f5f6fa; }
    .card { border-radius: 12px; }
    .kpi { font-size: 28px; font-weight: bold; }
    </style>

    </head>
    <body>

    <div class="container mt-4">

        <h2 class="mb-4">📊 Dashboard de Licitações</h2>

        <!-- KPI -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card p-3 shadow-sm">
                    <div>Total de Licitações</div>
                    <div class="kpi">{{total}}</div>
                </div>
            </div>
        </div>

        <!-- Busca -->
        <input class="form-control mb-3" id="search" placeholder="Buscar...">

        <!-- Tabela -->
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Data</th>
                    <th>Objeto</th>
                    <th>Link</th>
                    <th>Detectado em</th>
                </tr>
            </thead>
            <tbody id="tabela">
            {% for d in dados %}
                <tr>
                    <td>{{d.codigo}}</td>
                    <td>{{d.data}}</td>
                    <td>{{d.objeto}}</td>
                    <td><a href="{{d.link}}" target="_blank">Abrir</a></td>
                    <td>{{d.hora}}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

    </div>

    <script>
    document.getElementById("search").addEventListener("keyup", function() {
        let filtro = this.value.toLowerCase();
        let linhas = document.querySelectorAll("#tabela tr");

        linhas.forEach(l => {
            let texto = l.innerText.toLowerCase();
            l.style.display = texto.includes(filtro) ? "" : "none";
        });
    });
    </script>

    </body>
    </html>
    """

    return render_template_string(html, dados=dados[::-1], total=total)

# -------------------------
# START
# -------------------------

if __name__ == "__main__":
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

=======
from flask import Flask, render_template_string
import threading
import time
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

URL = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"

ARQUIVO_LOG = "historico.txt"
ARQUIVO_ESTADO = "estado.txt"

PALAVRAS = ["sapiranga", "dragagem", "ete"]

# -------------------------
# UTIL
# -------------------------

def salvar_log(msg):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def salvar_estado(itens):
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as f:
        f.write("\n".join(itens))

# -------------------------
# EXTRAIR OBJETO
# -------------------------

def extrair_objeto(pagina):
    linhas = pagina.split("\n")

    for i, linha in enumerate(linhas):
        if any(p in linha for p in ["objeto", "descrição", "referente", "finalidade"]):
            return " ".join(linhas[i:i+2])[:300]

    return ""

# -------------------------
# MONITOR
# -------------------------

def monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print("🔎 Monitor rodando...")

    while True:
        try:
            driver.get(URL)
            time.sleep(5)

            texto = driver.find_element("tag name", "body").text.lower()
            linhas = [l.strip() for l in texto.split("\n") if l.strip()]

            registros = []

            # EXTRAÇÃO DOS BLOCOS
            for i in range(len(linhas)):
                linha = linhas[i]

                if "/" in linha and any(c.isdigit() for c in linha):
                    codigo = linha
                    tipo = linhas[i+1] if i+1 < len(linhas) else ""
                    status = linhas[i+2] if i+2 < len(linhas) else ""
                    data_str = linhas[i+3] if i+3 < len(linhas) else ""

                    try:
                        data = datetime.strptime(data_str, "%d/%m/%Y")
                    except:
                        continue

                    registros.append({
                        "codigo": codigo,
                        "tipo": tipo,
                        "status": status,
                        "data": data,
                        "data_str": data_str
                    })

            # ORDENAÇÃO REAL
            registros.sort(key=lambda x: x["data"], reverse=True)

            # LIMITA A 10 MAIS RECENTES
            registros = registros[:10]

            itens_atuais = set()

            elementos = driver.find_elements("tag name", "a")

            for r in registros:
                codigo = r["codigo"]
                data_str = r["data_str"]

                link = ""

                # ASSOCIA LINK
                for el in elementos:
                    if codigo in el.text.lower():
                        link = el.get_attribute("href")
                        break

                objeto = ""

                # ABRE LINK PARA PEGAR OBJETO
                if link:
                    try:
                        driver.execute_script("window.open(arguments[0]);", link)
                        driver.switch_to.window(driver.window_handles[1])

                        time.sleep(3)

                        pagina = driver.find_element("tag name", "body").text.lower()
                        objeto = extrair_objeto(pagina)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])

                    except Exception as e:
                        print("Erro ao abrir link:", e)

                item = f"{codigo} | {data_str} | {objeto} | {link}"
                itens_atuais.add(item.lower())

            # COMPARAÇÃO
            itens_antigos = carregar_estado()
            novos = itens_atuais - itens_antigos

            if novos:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")

                for item in novos:
                    if any(p in item for p in PALAVRAS):
                        msg = f"{item} | {agora}"
                        print("🚨 Nova licitação:", msg)
                        salvar_log(msg)

                salvar_estado(itens_atuais)

        except Exception as e:
            print("Erro geral:", e)

        time.sleep(600)  # 10 minutos

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def home():
    dados = []

    try:
        with open(ARQUIVO_LOG, encoding="utf-8") as f:
            linhas = f.readlines()

        for linha in linhas:
            partes = linha.split("|")

            if len(partes) >= 5:
                dados.append({
                    "codigo": partes[0].strip(),
                    "data": partes[1].strip(),
                    "objeto": partes[2].strip(),
                    "link": partes[3].strip(),
                    "hora": partes[4].strip()
                })

    except:
        pass

    total = len(dados)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Dashboard Licitações</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
    body { background-color: #f5f6fa; }
    .card { border-radius: 12px; }
    .kpi { font-size: 28px; font-weight: bold; }
    </style>

    </head>
    <body>

    <div class="container mt-4">

        <h2 class="mb-4">📊 Dashboard de Licitações</h2>

        <!-- KPI -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card p-3 shadow-sm">
                    <div>Total de Licitações</div>
                    <div class="kpi">{{total}}</div>
                </div>
            </div>
        </div>

        <!-- Busca -->
        <input class="form-control mb-3" id="search" placeholder="Buscar...">

        <!-- Tabela -->
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Data</th>
                    <th>Objeto</th>
                    <th>Link</th>
                    <th>Detectado em</th>
                </tr>
            </thead>
            <tbody id="tabela">
            {% for d in dados %}
                <tr>
                    <td>{{d.codigo}}</td>
                    <td>{{d.data}}</td>
                    <td>{{d.objeto}}</td>
                    <td><a href="{{d.link}}" target="_blank">Abrir</a></td>
                    <td>{{d.hora}}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

    </div>

    <script>
    document.getElementById("search").addEventListener("keyup", function() {
        let filtro = this.value.toLowerCase();
        let linhas = document.querySelectorAll("#tabela tr");

        linhas.forEach(l => {
            let texto = l.innerText.toLowerCase();
            l.style.display = texto.includes(filtro) ? "" : "none";
        });
    });
    </script>

    </body>
    </html>
    """

    return render_template_string(html, dados=dados[::-1], total=total)

# -------------------------
# START
# -------------------------

if __name__ == "__main__":
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

>>>>>>> 5e6315be44943bb2a192d2327c9853d408c6fba7
    app.run(host="0.0.0.0", port=10000)