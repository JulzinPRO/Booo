from dotenv import load_dotenv
from telethon.sync import TelegramClient
import os
import asyncio
from fastapi import FastAPI
import uvicorn
import threading

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Bot Full Activado"}

@app.get("/status")
def status():
    return {"status": "Bot is active"}

async def get_list_of_groups(client):
    # Dummy implementation; replace with actual code to get groups
    return [{"group_id": 123456789, "group_name": "Example Group"}]

async def get_messages_from_group(client, group_id):
    # Dummy implementation; replace with actual code to get messages
    return ["Message 1", "Message 2", "Message 3"]

async def log_user_bot():
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
        try:
            groups_info = await get_list_of_groups(client)
            messages_list = await get_messages_from_group(client, spammer_group)

            await client.send_message("@botDoxing", f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list) - 1}</code>", parse_mode="HTML")

            excluded_groups = ["Spam 2024", "DOXEO ECONOMICO"]

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
            await asyncio.sleep(120)
        except Exception as e:
            print(f"Error general en el bucle del bot: {e}")

    await client.disconnect()

if __name__ == "__main__":
    # Run FastAPI app with uvicorn
    threading.Thread(target=lambda: uvicorn.run(app, host='0.0.0.0', port=4960)).start()
    # Run the Telegram bot
    asyncio.run(log_user_bot())
