import requests

# Tus credenciales oficiales integradas para evitar errores
TELEGRAM_TOKEN = "8924539176:AAFsJVsjgVH_KP4_r2HvJ_sa-DRSWMOnq1I"
TELEGRAM_CHAT_ID = "8093544374"

def send_telegram_alert(message, reply_markup=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando alerta Telegram: {e}")

def build_approval_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Aprobar Orden", "callback_data": "APPROVE_TRADE"},
                {"text": "❌ Rechazar", "callback_data": "REJECT_TRADE"}
            ]
        ]
    }