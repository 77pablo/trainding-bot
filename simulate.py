import time
from datetime import datetime
import sqlite3
from telegram_notifier import send_telegram_alert, build_approval_buttons

print("🚀 [SIMULADOR] Iniciando simulación de QuantBot V9...")

# 1. Simular datos de mercado actuales
simulated_symbol = "BTC/USDT"
simulated_price = 76500.0
simulated_action = "BUY"
allocated_capital = 100.0

print(f"📊 Analizando par: {simulated_symbol} | Precio: ${simulated_price} | Señal: {simulated_action}")
time.sleep(1)

# 2. Calcular riesgo simulado con comisiones reales
sl_price = simulated_price * (1 - 0.015)
tp_price = simulated_price * (1 + 0.030)
net_profit = allocated_capital * 0.030 - (allocated_capital * 0.0008)

print(f"🛡️ Gestión de Riesgo Aplicada:")
print(f"   - Stop Loss (1.5%): ${round(sl_price, 2)}")
print(f"   - Take Profit Neto (3% - Comisiones): +${round(net_profit, 2)} USDT")
time.sleep(1)

# 3. Enviar Alerta Interactiva a Telegram
print("\n📱 Enviando alerta interactiva a Telegram (@pablo_traiding_bot)...")
mensaje = (
    f"🚨 *[SIMULACIÓN] OPORTUNIDAD DETECTADA*\n\n"
    f"• **Activo:** {simulated_symbol}\n"
    f"• **Señal:** {simulated_action} (Filtro Macro 4h: OK 🟢)\n"
    f"• **Precio de Entrada:** ${simulated_price}\n"
    f"• **Ganancia Neta Est.:** +${round(net_profit, 2)} USDT\n\n"
    f"¿Deseas aprobar la ejecución de esta orden simulada?"
)
send_telegram_alert(mensaje, build_approval_buttons())
print("✅ Alerta enviada a tu celular. ¡Revisa Telegram!")

# 4. Registrar de forma persistente en SQLite (quantbot.db)
print("\n💾 Registrando operación simulada en la base de datos (quantbot.db)...")
conn = sqlite3.connect("quantbot.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        timestamp TEXT NOT NULL, 
        symbol TEXT NOT NULL, 
        price REAL NOT NULL, 
        action TEXT NOT NULL, 
        mode TEXT NOT NULL
    )
''')
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cursor.execute("INSERT INTO trades (timestamp, symbol, price, action, mode) VALUES (?, ?, ?, ?, ?)",
               (now, simulated_symbol, simulated_price, simulated_action, "SIMULACIÓN"))
conn.commit()
cursor.close()
conn.close()
print("✅ Operación guardada permanentemente en SQLite.")
print("\n🎉 ¡Simulación completada con éxito! Tu panel web y Telegram están sincronizados.")