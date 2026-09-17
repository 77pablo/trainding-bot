from telegram_notifier import send_telegram_alert, build_approval_buttons

print("🚀 Enviando alerta de prueba con botones interactivos a Telegram...")
mensaje_prueba = "🚨 *PRUEBA DE SISTEMA QUANTBOT V9*\n\n¡La conexión con Telegram funciona a la perfección! ¿Deseas aprobar esta señal de prueba?"

send_telegram_alert(mensaje_prueba, build_approval_buttons())
print("✅ ¡Mensaje enviado! Revisa tu celular.")