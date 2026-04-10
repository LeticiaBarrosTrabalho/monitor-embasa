import re
import pytz
import chompjs
import pandas as pd
import time
import requests

from bs4 import BeautifulSoup
from plyer import notification

# CONFIG
URL = "https://www.embasa.ba.gov.br/fornecedor/navigate.do?sys=FOR&formID=464569229&componentID=1006869&action=navigate&inner=true&gt="
INTERVALO = 300

# FUSO HORÁRIO BRASIL
fuso = pytz.timezone("America/Sao_Paulo")
    
def extrair_variaveis_js(texto):
    resultado = {}
    # Encontra todos os padrões: nome_variavel = [... ou {...
    matches = re.finditer(r'(\w+)\s*=\s*([{\[])', texto)
    
    # Chompjs trata a primeira variavel JS encontrada
    # Então encontro a variavel e faço o chompjs tratar todo o resto do conteúdo a partir dela
    for match in matches:
        # Aqui fica o nome da variável
        nome = match.group(1)
        
        # Pega o conteúdo a partir do { ou [ encontrado
        inicio = match.start(2)
        
        # Transforma em um objeto no python
        # Pode ser necessario outras transformações alem do replace
        valor = chompjs.parse_js_object(texto[inicio:].replace('\t', '\\t'))
        
        # Salve como um dict pra ser mais facil de acessar
        resultado[nome] = valor
    return resultado

def extrair_dados():
    print('\t 🟡 Extraindo dados... (notificações travadas)')
    n_pagina = 1 # contador de paginas pro parametro gt da URL
    final_df = [pd.DataFrame()] # lista de dataframes para concatenar depois, dataframe vazio pra facilitar comparação da primeira página (AKA gambiarra)

    while True:
        #############################
        # ENCONTRA AS INFOS NO HTML #
        #############################    
        request_url = URL + str(n_pagina*100) ## Esse é o formato da requisição, pergunta pro gov pq é assim
        
        ## Faz a requisição e extrai as variáveis JS da resposta
        r = requests.get(request_url)
        soup = BeautifulSoup(r.text, "html.parser")
        variaveis_tabela = extrair_variaveis_js(r.text)
        # Infos de coluna estão em cols_1006869    
        # Infos de dados estão em data_1006869
        cols = variaveis_tabela['cols_1006869']
        data = variaveis_tabela['data_1006869']
        
        ########################################################################
        # AJUSTA O DATAFRAME PARA O FORMATO CORRETO, USANDO OS DADOS EXTRAIDOS #
        ########################################################################
        ## Requisição traz o nome das colunas
        col_dict_mapping = {col['name']: col['title'] for col in cols}
        
        ## Monta o dataframe e ajusta o nome das colunas
        df = pd.DataFrame(data).rename(columns=col_dict_mapping).drop(columns=['row'])
        
        if df.empty:
            break ## Se a página não tiver dados, acabou a extração
        
        elif df.equals(final_df[-1]):
            break ## Se a página tiver os mesmos dados da última, acabou a extração
        
        else:    
            ## Append numa lista de dataframes para concatenar depois
            final_df.append(df)
            n_pagina += 1

            time.sleep(1) # Evitar bater o limite de requisições do servidor
        
    final_df = pd.concat(final_df, ignore_index=True).sort_index(ascending = False)
    
    df_envio = \
    final_df[["Edital", "Unidade Demandante", "Objeto", "Abertura"]].rename(columns = {"Edital": "codigo", 
                                                                                    "Unidade Demandante": "nome", 
                                                                                    "Objeto": "objeto", 
                                                                                    "Abertura": "data"})
    
    df_envio["link"] = "https://www.embasa.ba.gov.br/fornecedor/navigate.do?sys=FOR&formID=464569229"
    
    print('\t 🟡 Extração realizada...')

    
    return df_envio.to_dict(orient="records")