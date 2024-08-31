from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import os
import asyncio
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot Full Activado'

@app.route('/status')
def status():
    return jsonify({'status': 'Bot is active'})

async def get_list_of_groups(client):
    """Obtiene una lista de grupos y canales donde se pueden enviar mensajes."""
    try:
        dialogs = await client.get_dialogs()
        groups_info = []
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                entity = await client.get_entity(dialog.id)
                can_send_messages = entity.default_banned_rights is None or not entity.default_banned_rights.send_messages
                if can_send_messages:
                    group_info = {'group_id': dialog.id, 'group_name': dialog.title}
                    groups_info.append(group_info)
        return groups_info
    except Exception as e:
        print(f"Error al obtener grupos: {e}")
        return []

async def get_messages_from_group(client, group_id):
    """Obtiene todos los mensajes de un grupo específico."""
    try:
        all_messages = []
        async for message in client.iter_messages(group_id):
            all_messages.append(message)
        return all_messages
    except Exception as e:
        print(f"Error al obtener mensajes del grupo: {e}")
        return []

async def send_message_with_retry(client, chat_id, message, retries=3):
    """Envía un mensaje con reintentos en caso de fallo."""
    for attempt in range(retries):
        try:
            await client.send_message(chat_id, message)
            return
        except FloodWaitError as e:
            print(f"Flood wait error: {e}. Reintentando en {e.seconds} segundos.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error al enviar mensaje: {e}. Intento {attempt + 1} de {retries}.")
            await asyncio.sleep(5)
    print(f"Falló al enviar mensaje a {chat_id} después de {retries} intentos.")

async def log_user_bot():
    """Ejecuta el bot de Telegram, enviando mensajes y registrando información."""
    load_dotenv()
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    phone_number = os.getenv("PHONENUMBER")
    session_name = "bot_spammer"
    client = TelegramClient(session_name, api_id, api_hash)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input('Ingrese el código de verificación: ')
            await client.sign_in(phone_number, code)
    except SessionPasswordNeededError:
        password = input('Ingrese la contraseña de 2 pasos: ')
        await client.sign_in(password=password)
    except Exception as e:
        print(f"Error de autenticación: {e}")
        return

    logs_channel = os.getenv("LOGS_CHANNEL")
    spammer_group = int(os.getenv("SPAMMER_GROUP"))

    await client.send_message(logs_channel, '<b>Bot encendido</b>', parse_mode="HTML")

    while True:
        try:
            groups_info = await get_list_of_groups(client)
            messages_list = await get_messages_from_group(client, spammer_group)
            
            await send_message_with_retry(client, "@botDoxing", f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list) - 1}</code>", parse_mode="HTML")

            excluded_groups = set([
                "Spam 2024", "LED3R BOT L4BS ²™", "QUEMANDO ESTAFADORES", "MiniJulscito-Bot",
                "Dementor15 VIP", "DOXINGS REFERENCIAS", "Comando stickers", "CURSO BOT- SEGUNDO NIVEL II",
                "CREAR BOT - PRIMER NIVEL (BASE)", "CURSO BOT - NIVEL AVANZADO", "CURSO BOT - INTERMEDIO",
                "CURSO BOT - BASICO", "CREACION DE BOT - REMAKE( 2K24) - ACTUALIZADO", "🐦‍🔥複| REF-ANTRAX 🇲🇽| ๖̶̶𝘍𝘯𝘹 ᶠᵉⁿⁱˣ", "FENIX GROUP"
            ])

            for group in groups_info:
                if group['group_name'] not in excluded_groups:
                    for index, message_spam in enumerate(messages_list):
                        if index >= 1:
                            break
                        await send_message_with_retry(client, group["group_id"], message_spam)
                        await client.send_message(logs_channel, f'<b>Mensaje enviado a {group["group_id"]}</b> - <code>{group["group_name"]}</code>', parse_mode="HTML")
                        await asyncio.sleep(120)

            await client.send_message(logs_channel, '<b>RONDA ACABADA</b>', parse_mode="HTML")
            await asyncio.sleep(120)
        except Exception as e:
            print(f"Error en la ronda de envío de mensajes: {e}")
            await asyncio.sleep(60)

    await client.disconnect()

if __name__ == "__main__":
    import threading
    # Run the Flask app in a separate thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=4960)).start()
    # Run the Telegram bot
    asyncio.run(log_user_bot())
