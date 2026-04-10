import time
import requests
from bs4 import BeautifulSoup
from scraping import extrair_dados
from plyer import notification
from datetime import datetime

URL_SITE = "https://www.embasa.ba.gov.br/fornecedor/form.jsp?sys=FOR&action=openform&formID=464569229"
URL_API = "https://monitor-embasa.onrender.com/novo"
URL_DADOS = "https://monitor-embasa.onrender.com/dados"

vistos = set()

def notificar(msg):
    try:
        notification.notify(
            title="🚨 EMBASA",
            message=msg,
            timeout=10
        )
    except:
        pass

def recuperar_antigos(warning = False):
    try:
        dados = requests.get(URL_DADOS, timeout=20).json()
        if warning:
            for item in dados[:5]:
                notificar(f"Anterior: {item['codigo']}")
            
        return dados
    except:
        return None

def monitor():
    print("🟢 Monitor rodando...")

    ###################################
    # RECUPERAÇÃO DOS DADOS "ANTIGOS" #
    ###################################
    dados_antigos = recuperar_antigos(warning = True)
    
    if dados_antigos:    
        for item in dados_antigos:
            vistos.add(item["codigo"])
    
    print("🟢 Dados antigos recuperados...")

    ###############################################
    # DEFINIÇÃO DE VARIAVEIS DE CONTROLE DE TEMPO #
    ###############################################
    t_scraping = 1800 # Tempo entre cada scraping (em segundos), pode esculachar pra bastante tempo
    t_sleep = 30 # Dimensionar baseado no onrender, para evitar sobrecarga de requisições
    
    t_last_scraping = 0 # Variável para controlar o tempo do último scraping
    
    while True:
        try:
            ##############################################
            # REALIZA O SCRAPING EM INTERVALOS DEFINIDOS #
            ##############################################
            t_now = datetime.now().timestamp()
            
            if (t_now - t_last_scraping) >= (t_scraping):                
                ############
                # SCRAPING #
                ############
                itens = extrair_dados()
                print('''\t 🟡 Verificando novos itens (notificações travadas)...''')                
                
                ###########################
                # NOTIFICAÇÕES DO WINDOWS #
                ###########################
                novos_itens = []
                for item in itens:
                    ## Compila os itens vistos
                    if item["codigo"] not in vistos:
                        vistos.add(item["codigo"])
                        requests.post(URL_API, json=item, timeout=20)
                        novos_itens.append([item['codigo'], item['nome']])                        
                    
                ## Notifica os novos itens baseado no número de itens novos encontrados
                # Se maior que ou igual a 30 agrupa tudo em uma notificação
                # Se menor que 30 notifica um por um                    
                if len(novos_itens) >= 30:
                    print("\t 🟡 Notificando alterações (Scraping)...")
                    
                    notificar(f"Novos itens encontrados e adicionados: {len(novos_itens)}")
                    
                elif len(novos_itens) > 0:
                    print("\t 🟡 Notificando alterações (Scraping)...")
                    
                    for item in novos_itens:
                        notificar(f"Novo (Scraping): {item[0]} - {item[1]}")
                        
                else:
                    pass
                
                t_last_scraping = datetime.now().timestamp()
            
            else:
                print(f"\t 🟡 {round((t_now - t_last_scraping), 2)}s do último scraping, pulando etapa...")
            
            print("\t 🟡 Verificando alterações fora do monitor...")
            check_onrender = recuperar_antigos()
            if any(item["codigo"] not in vistos for item in check_onrender):
                print("\t 🟡 Notificando alterações (OnRender)...")
            for item in check_onrender:
                if item["codigo"] not in vistos:
                    vistos.add(item["codigo"])
                    notificar(f"Novo (OnRender): {item['codigo']} - {item['nome']}")
                    
            print("\t 🟡 Verificação concluída.")
            
            
            
        except Exception as e:
            print("Erro:", e)

        print(f'\t 🟡 Aguardando próxima verificação... ({t_sleep} segundos)\n')
        time.sleep(t_sleep)

monitor()