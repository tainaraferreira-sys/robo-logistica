import time
import requests
from playwright.sync_api import sync_playwright
from datetime import datetime

def rodar_robo():
    # URL DO SEU WEBHOOK
    WEBHOOK_URL = "SUA_URL_AQUI" 
    
    # Formata a data para o relatório
    hoje = datetime.now().strftime('%d/%m/%Y')
    mes_vigente = datetime.now().strftime('%b/%y').capitalize() 

    with sync_playwright() as p:
        print("Abrindo navegador...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Acessa o Dashboard
        page.goto("https://spontaneous-valkyrie-a731ef.netlify.app/")
        
        # Espera o carregamento dos dados
        time.sleep(12) 
        
        # Tira o print (ele fica salvo no GitHub como backup, mesmo não indo no chat)
        page.screenshot(path="status_atual.png")
        
        browser.close()

    # MONTAGEM DA MENSAGEM (O "PULO DO GATO")
    payload = {
        "text": (
            f"📦 *BOLETIM DIÁRIO - LOGÍSTICA* 📦\n"
            f"__________________________________\n\n"
            f"📅 *Data:* {hoje}\n"
            f"📊 *Mês de Referência:* {mes_vigente}\n"
            f"✅ *Status:* Dados atualizados no sistema.\n\n"
            f"👇 *Acesse o Dashboard completo aqui:*\n"
            f"https://spontaneous-valkyrie-a731ef.netlify.app/\n"
            f"__________________________________"
        )
    }
    
    # Envia para o Google Chat
    requests.post(WEBHOOK_URL, json=payload)
    print("Relatório enviado!")

if __name__ == "__main__":
    rodar_robo()
