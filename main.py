import time
import requests
import base64
from playwright.sync_api import sync_playwright
from datetime import datetime

def rodar_robo():
    # 1. COLOQUE SEU WEBHOOK AQUI
    WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAsU0dFDo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=MFIwEiw61ezL9BEA67igqnytNsShx71-HlmtcoNgFn4"
    
    # 2. CHAVE PARA IMAGEM (Essa é uma chave pública de teste, pode usar)
    IMGBB_KEY = "9390234b8686d0a7f14798539075e7a9"

    hoje = datetime.now().strftime('%d/%m/%Y')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto("https://spontaneous-valkyrie-a731ef.netlify.app/")
        time.sleep(15) # Tempo pro dash carregar
        
        # Tira o print e guarda na memória do robô
        screenshot_bytes = page.screenshot(full_page=False)
        browser.close()

    # 3. FAZ O UPLOAD DA IMAGEM PARA ELA VIRAR UM LINK
    print("Subindo imagem para o servidor...")
    img_base64 = base64.b64encode(screenshot_bytes)
    res = requests.post("https://api.imgbb.com/1/upload", 
                        data={"key": IMGBB_KEY, "image": img_base64})
    link_da_foto = res.json()["data"]["url"]

    # 4. MANDA PRO GOOGLE CHAT COM A FOTO APARECENDO
    payload = {
        "cardsV2": [{
            "cardId": "relatorio_logistica",
            "card": {
                "header": {
                    "title": "📦 BOLETIM LOGÍSTICA",
                    "subtitle": f"Data: {hoje}",
                    "imageUrl": "https://fonts.gstatic.com/s/i/googlematerialicons/insert_chart/v18/24px.svg"
                },
                "sections": [{
                    "widgets": [
                        {"image": {"imageUrl": link_da_foto}},
                        {"buttonList": {
                            "buttons": [{
                                "text": "ABRIR DASHBOARD",
                                "onClick": {"openLink": {"url": "https://spontaneous-valkyrie-a731ef.netlify.app/"}}
                            }]
                        }}
                    ]
                }]
            }
        }]
    }
    
    requests.post(WEBHOOK_URL, json=payload)
    print("Pronto! Agora a foto vai aparecer!")

if __name__ == "__main__":
    rodar_robo()
