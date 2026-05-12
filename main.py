import os
import time
from playwright.sync_api import sync_playwright
import yagmail
from datetime import datetime

def capturar_e_enviar():
    hoje = datetime.now().strftime('%d/%m/%Y')
    
    with sync_playwright() as p:
        print("Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        # Acessa o Dashboard
        page.goto("https://spontaneous-valkyrie-a731ef.netlify.app/")
        time.sleep(15) # Espera carregar os dados
        
        # Tira o print
        path_print = "status_logistica.png"
        page.screenshot(path=path_print, full_page=False)
        browser.close()
        
    print("Enviando e-mail com o print...")
    
    # --- CONFIGURAÇÃO ---
    meu_email = "SEU_EMAIL@gmail.com" # <--- Seu Gmail
    # Pega a senha que você salvou no Settings > Secrets do GitHub
    senha_segura = os.environ.get('EMAIL_PASSWORD') 
    
    try:
        usuario = yagmail.SMTP(meu_email, senha_segura)
        usuario.send(
            to=meu_email, # Manda para você mesma
            subject=f"📊 Print do Dashboard - {hoje}",
            contents=f"Olá! Segue o print do Dashboard de Logística tirado hoje ({hoje}).",
            attachments=path_print
        )
        print("Sucesso! Verifique seu e-mail.")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

if __name__ == "__main__":
    capturar_e_enviar()
