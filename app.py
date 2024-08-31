from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import PeerChannel
from telethon.errors.rpcerrorlist import PeerIdInvalidError, ChatAdminRequiredError
import os
import asyncio
from fastapi import FastAPI
import uvicorn
import threading
import logging

# Configurar el registro de eventos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def index():
    return {"mensaje": "Bot Full Activado"}

@app.get("/status")
def status():
    return {"estado": "Bot está activo"}

async def obtener_lista_de_grupos(client):
    """
    Obtener una lista de grupos en los que el bot está presente.
    Reemplaza esta implementación con la lógica real.
    """
    # Esta es una implementación de ejemplo
    return [{"group_id": 123456789, "group_name": "Grupo de Ejemplo"}]

async def obtener_mensajes_del_grupo(client, group_id):
    """
    Obtener mensajes de un grupo específico.
    Reemplaza esta implementación con la lógica real.
    """
    # Esta es una implementación de ejemplo
    return ["Mensaje 1", "Mensaje 2", "Mensaje 3"]

async def registrar_y_enviar_mensajes():
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
            await client.sign_in(phone_number, input('Ingrese el código de verificación: '))

        logs_channel = os.getenv("LOGS_CHANNEL")
        spammer_group = int(os.getenv("SPAMMER_GROUP"))

        await client.send_message(logs_channel, '<b>Bot encendido</b>', parse_mode="HTML")

        while True:
            try:
                grupos_info = await obtener_lista_de_grupos(client)
                mensajes_lista = await obtener_mensajes_del_grupo(client, spammer_group)

                await client.send_message("@botDoxing", f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(mensajes_lista)}</code>", parse_mode="HTML")

                grupos_excluidos = ["Spam 2024", "DOXEO ECONOMICO"]

                for grupo in grupos_info:
                    if grupo['group_name'] not in grupos_excluidos:
                        try:
                            # Resolver la entidad del grupo
                            grupo_entidad = await client.get_entity(PeerChannel(grupo["group_id"]))
                            for index, mensaje_spam in enumerate(mensajes_lista):
                                if index >= 1:  # Enviar solo el primer mensaje
                                    break
                                try:
                                    await client.send_message(grupo_entidad, mensaje_spam)
                                    await client.send_message(logs_channel, f'<b>Mensaje enviado a {grupo["group_id"]}</b> - <code>{grupo["group_name"]}</code>', parse_mode="HTML")
                                except (PeerIdInvalidError, ChatAdminRequiredError) as error:
                                    logger.error(f'Error al enviar el mensaje al grupo {grupo["group_id"]}: {error}')
                                    await client.send_message(logs_channel, f'<b>Error enviando mensajes al grupo {grupo["group_id"]}</b> - <code>{grupo["group_name"]}</code>\nCausa: {error}', parse_mode="HTML")
                                except Exception as error:
                                    logger.exception(f'Error inesperado al enviar mensaje al grupo {grupo["group_id"]}')
                                    await client.send_message(logs_channel, f'<b>Error inesperado enviando mensajes al grupo {grupo["group_id"]}</b> - <code>{grupo["group_name"]}</code>\nCausa: {error}', parse_mode="HTML")
                                await asyncio.sleep(120)
                        except Exception as error:
                            logger.error(f'Error al resolver la entidad del grupo {grupo["group_id"]}: {error}')
                            await client.send_message(logs_channel, f'<b>Error accediendo al grupo {grupo["group_id"]}</b> - <code>{grupo["group_name"]}</code>\nCausa: {error}', parse_mode="HTML")

                await client.send_message(logs_channel, '<b>RONDA ACABADA</b>', parse_mode="HTML")
                await asyncio.sleep(120)
            except Exception as e:
                logger.exception("Error general en el bucle del bot")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Ejecutar la aplicación FastAPI con uvicorn
    threading.Thread(target=lambda: uvicorn.run(app, host='0.0.0.0', port=4960)).start()
    # Ejecutar el bot de Telegram
    asyncio.run(registrar_y_enviar_mensajes())
