import time
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

def capturar_e_postar_no_chat():
    mes_atual = datetime.now().strftime('%b/%y').capitalize() 
    webhook_url = "COLE_AQUI_A_URL_DO_WEBHOOK_DO_GOOGLE_CHAT"

    with sync_playwright() as p:
        print("Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        
        page.goto("https://spontaneous-valkyrie-a731ef.netlify.app/")
        time.sleep(15) # Tempo para o Dash carregar
        
        try:
            page.select_option('select', label=mes_atual)
            time.sleep(5)
        except:
            print("Filtro de mês não encontrado.")

        # Tira o print e salva
        path_print = "status.png"
        page.screenshot(path=path_print)
        browser.close()

    # Envia para o Google Chat
    # Nota: O Webhook simples do Google Chat aceita texto. 
    # Para mandar IMAGEM via Webhook, o texto precisa conter o link da imagem ou usar a API avançada.
    # Por enquanto, vamos mandar o aviso e o status em texto para testar:
    
    texto_mensagem = f"📊 *Dashboard Atualizado ({datetime.now().strftime('%d/%m/%Y')})*\nStatus: Filtrado para {mes_atual}\nLink: https://spontaneous-valkyrie-a731ef.netlify.app/"
    
    requests.post(webhook_url, json={"text": texto_mensagem})
    print("Mensagem enviada ao Google Chat!")

if __name__ == "__main__":
    capturar_e_postar_no_chat()
