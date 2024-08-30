from dotenv import load_dotenv
from telethon.sync import TelegramClient
import os
import asyncio
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot Full Activado'

@app.route('/status')
def status():
    return 'Bot is active'

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
            try:
                all_messages.append(message)
            except Exception as e:
                print(f"Error al procesar mensaje: {e}")
        return all_messages
    except Exception as e:
        print(f"Error al obtener mensajes del grupo: {e}")
        return []

async def log_user_bot():
    """Ejecuta el bot de Telegram, enviando mensajes y registrando información."""
    load_dotenv()
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    phone_number = os.getenv("PHONENUMBER")
    session_name = "bot_spammer"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Ingrese el código de verificación: '))

    logs_channel = os.getenv("LOGS_CHANNEL")
    spammer_group = int(os.getenv("SPAMMER_GROUP"))

    await client.send_message(logs_channel, '<b>Bot encendido</b>', parse_mode="HTML")

    while True:
        groups_info = await get_list_of_groups(client)
        messages_list = await get_messages_from_group(client, spammer_group)

        try:
            await client.send_message("@botDoxing", f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list) - 1}</code>", parse_mode="HTML")
        except Exception as e:
            print(f"Error al enviar mensaje a @botDoxing: {e}")

        try:
            excluded_groups = ["Spam 2024","DOXEO ECONOMICO"]

            for group in groups_info:
                if group['group_name'] not in excluded_groups:
                    for index, message_spam in enumerate(messages_list):
                        if index >= 1:  # Enviar solo el primer mensaje
                            break
                        try:
                            await client.send_message(group["group_id"], message_spam)
                            await client.send_message(logs_channel, f'<b>Mensaje enviado a {group["group_id"]}</b> - <code>{group["group_name"]}</code>', parse_mode="HTML")
                        except Exception as error:
                            await client.send_message(logs_channel, f'<b>Error enviando mensajes a {group["group_id"]}</b> - <code>{group["group_name"]}</code>\nCausa: {error}', parse_mode="HTML")
                        await asyncio.sleep(120)

            await client.send_message(logs_channel, '<b>RONDA ACABADA</b>', parse_mode="HTML")
            await asyncio.sleep(300)
        except Exception as e:
            print(f"Error en la ronda de envío de mensajes: {e}")

    await client.disconnect()

if __name__ == "__main__":
    import threading
    # Run the Flask app in a separate thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=4960)).start()
    # Run the Telegram bot
    asyncio.run(log_user_bot())
