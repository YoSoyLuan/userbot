from telethon import TelegramClient, events, utils, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetAllStickersRequest, SearchGlobalRequest
from telethon.tl.functions.channels import GetParticipantsRequest, JoinChannelRequest
from telethon.tl.types import ChannelParticipantsSearch, User, Chat, Channel, InputMessagesFilterPhotos
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.errors import FloodWaitError, ChatAdminRequiredError
from datetime import datetime, timedelta
import asyncio
import platform
import psutil
import time
# Modifica tu código para usar variables de entorno
import os
API_ID = '27468249'
API_HASH = '458281447ab71aa601870024f635464c'
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
import sys
import wikipedia
import random
import json
import math
import requests
import io
import aiohttp
from urllib.parse import quote_plus
import re
from PIL import Image
from collections import defaultdict

# Configuración
API_ID = "27468249"
API_HASH = "458281447ab71aa601870024f635464c"
SESSION_NAME = "mi_userbot_session"
NOTAS_FILE = "notas.json"
WEATHER_API_KEY = "4d954a9a99106fe0884565f24936a7b0"  # Para OpenWeatherMap
SUDO_USERS = []  # Lista de IDs de usuarios con acceso a comandos administrativos
PREFIJO = "."  # Prefijo para comandos

# Inicializar el cliente
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Cargar notas
if os.path.exists(NOTAS_FILE):
    with open(NOTAS_FILE, 'r', encoding='utf-8') as f:
        notas = json.load(f)
else:
    notas = {}

# Funciones de utilidad
def guardar_notas():
    with open(NOTAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(notas, f, ensure_ascii=False, indent=2)

def format_bytes(size):
    power = 2**10
    n = 0
    units = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}B"

def calculate_account_age(creation_date):
    now = datetime.now()
    diff = now - creation_date
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30
    return years, months, days

async def progress_callback(current, total, event, start_time, info):
    if not total:
        return
    now = time.time()
    diff = now - start_time
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        eta = round((total - current) / speed)
        progress_str = "[{0}{1}] {2}%".format(
            "".join("█" for _ in range(math.floor(percentage / 5))),
            "".join("░" for _ in range(20 - math.floor(percentage / 5))),
            round(percentage, 2))
        await event.edit(f"{info}\n{progress_str}\nCompletado: {format_bytes(current)}/{format_bytes(total)}")

# Comandos básicos
@client.on(events.NewMessage(pattern=f'{PREFIJO}ping'))
async def ping_handler(event):
    start = datetime.now()
    message = await event.reply('Pong!')
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await message.edit(f'¡Pong! 🏓\nLatencia: `{ms}ms`')

@client.on(events.NewMessage(pattern=f'{PREFIJO}alive'))
async def alive_handler(event):
    uname = platform.uname()
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    mensaje = (
        "🤖 **Estado del UserBot**\n\n"
        f"🖥️ **Sistema:** `{uname.system}`\n"
        f"💻 **Host:** `{uname.node}`\n"
        f"🔋 **CPU:** `{psutil.cpu_percent()}%`\n"
        f"💾 **RAM:** `{psutil.virtual_memory().percent}%`\n"
        f"⚡ **Python:** `{platform.python_version()}`\n"
        f"⏱️ **Uptime:** `{str(uptime).split('.')[0]}`\n"
        "✅ Bot funcionando correctamente!"
    )
    await event.reply(mensaje)

# Sistema de notas
@client.on(events.NewMessage(pattern=f'{PREFIJO}guardarnota (.+)'))
async def save_note_handler(event):
    nombre_nota = event.pattern_match.group(1)
    mensaje = await event.get_reply_message()
    
    if not mensaje:
        await event.reply("❌ Responde a un mensaje para guardarlo como nota.")
        return
    
    notas[nombre_nota] = {
        'texto': mensaje.text,
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    guardar_notas()
    await event.reply(f"✅ Nota '{nombre_nota}' guardada correctamente.")

@client.on(events.NewMessage(pattern=f'{PREFIJO}nota (.+)'))
async def get_note_handler(event):
    nombre_nota = event.pattern_match.group(1)
    if nombre_nota in notas:
        nota = notas[nombre_nota]
        await event.reply(f"📝 **Nota:** {nombre_nota}\n📅 **Guardada:** {nota['fecha']}\n\n{nota['texto']}")
    else:
        await event.reply(f"❌ No existe ninguna nota llamada '{nombre_nota}'")

# Comandos de información de usuario
@client.on(events.NewMessage(pattern=f'{PREFIJO}userinfo(?:\s+(.+))?'))
async def user_info_handler(event):
    try:
        input_str = event.pattern_match.group(1)
        
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            user_id = reply_message.sender_id
        elif input_str:
            try:
                if input_str.isdigit():
                    user_id = int(input_str)
                else:
                    user_id = input_str.strip('@')
            except ValueError:
                await event.reply("❌ ID de usuario inválido")
                return
        else:
            user_id = event.sender_id
        
        user = await client.get_entity(user_id)
        full_user = await client(GetFullUserRequest(user.id))
        
        # Calcular edad de la cuenta
        creation_date = user.date
        years, months, days = calculate_account_age(creation_date)
        
        info = [
            "👤 **INFORMACIÓN DETALLADA DEL USUARIO**\n",
            f"**🆔 ID:** `{user.id}`",
            f"**👤 Nombre:** {user.first_name}",
            f"**📅 Fecha exacta de creación:** `{creation_date.strftime('%Y-%m-%d %H:%M:%S')}`",
            f"**⏳ Edad de la cuenta:** {years} años, {months} meses, {days} días"
        ]
        
        if user.last_name:
            info.append(f"**📝 Apellido:** {user.last_name}")
        if user.username:
            info.append(f"**🔤 Username:** @{user.username}")
        if full_user.about:
            info.append(f"**ℹ️ Bio:** {full_user.about}")
        if user.bot:
            info.append("**🤖 Este usuario es un bot**")
        if user.verified:
            info.append("**✅ Usuario verificado**")
        if user.scam:
            info.append("**⚠️ ADVERTENCIA: Usuario marcado como SCAM**")
        
        await event.reply("\n".join(info))
        
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Comandos de administración de chat
@client.on(events.NewMessage(pattern=f'{PREFIJO}purge'))
async def purge_handler(event):
    if not event.reply_to_msg_id:
        await event.reply("❌ Responde al mensaje desde donde quieres empezar a borrar.")
        return
    
    messages = []
    mensaje_count = 0
    
    async for mensaje in client.iter_messages(
        event.chat_id,
        min_id=event.reply_to_msg_id,
        from_user="me"
    ):
        messages.append(mensaje)
        mensaje_count += 1
        if len(messages) == 100:
            await client.delete_messages(event.chat_id, messages)
            messages = []
    
    if messages:
        await client.delete_messages(event.chat_id, messages)
    
    notification = await event.reply(f"🗑️ Eliminados {mensaje_count} mensajes.")
    await asyncio.sleep(3)
    await notification.delete()

# Comandos de búsqueda
@client.on(events.NewMessage(pattern=f'{PREFIJO}wiki (.+)'))
async def wikipedia_handler(event):
    busqueda = event.pattern_match.group(1)
    try:
        wikipedia.set_lang("es")
        resultado = wikipedia.summary(busqueda, sentences=5)
        await event.reply(f"🔍 **Búsqueda:** {busqueda}\n\n{resultado}")
    except Exception as e:
        await event.reply(f"❌ Error: No se encontró información sobre '{busqueda}'")

@client.on(events.NewMessage(pattern=f'{PREFIJO}clima (.+)'))
async def weather_handler(event):
    try:
        ciudad = event.pattern_match.group(1)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={quote_plus(ciudad)}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
        if data['cod'] == 200:
            weather = [
                f"🌡️ **Clima en {data['name']}, {data['sys']['country']}**\n",
                f"**🌤️ Condición:** {data['weather'][0]['description']}",
                f"**🌡️ Temperatura:** {data['main']['temp']}°C",
                f"**💧 Humedad:** {data['main']['humidity']}%",
                f"**🌪️ Viento:** {data['wind']['speed']} m/s",
                f"**☁️ Nubes:** {data['clouds']['all']}%"
            ]
            await event.reply("\n".join(weather))
        else:
            await event.reply("❌ Ciudad no encontrada")
            
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Comandos de diversión
@client.on(events.NewMessage(pattern=f'{PREFIJO}dado'))
async def dice_handler(event):
    numero = random.randint(1, 6)
    dados = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
    await event.reply(f"🎲 {dados[numero-1]} ({numero})")

@client.on(events.NewMessage(pattern=f'{PREFIJO}moneda'))
async def coin_handler(event):
    resultado = random.choice(['Cara 🗽', 'Cruz 🏛️'])
    await event.reply(f"🪙 La moneda cayó en: {resultado}")

# Comandos de sistema
@client.on(events.NewMessage(pattern=f'{PREFIJO}sysinfo'))
async def sysinfo_handler(event):
    try:
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        cpu_freq = psutil.cpu_freq()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        sysinfo = [
            "🖥️ **INFORMACIÓN DEL SISTEMA**\n",
            f"**💻 Sistema:** {uname.system}",
            f"**🔄 Procesador:** {uname.processor}",
            f"**⚡ CPU Frecuencia:** {cpu_freq.current:.2f}Mhz",
            f"**🔋 CPU Uso:** {psutil.cpu_percent()}%",
            f"**💾 RAM Total:** {format_bytes(memory.total)}",
            f"**💾 RAM Uso:** {memory.percent}%",
            f"**💿 Disco Total:** {format_bytes(disk.total)}",
            f"**💿 Disco Uso:** {disk.percent}%",
            f"**⏰ Tiempo de actividad:** {datetime.now() - boot_time}"
        ]
        
        await event.reply("\n".join(sysinfo))
        
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")

# Comando de ayuda
@client.on(events.NewMessage(pattern=f'{PREFIJO}help'))
async def help_handler(event):
    help_text = """
🤖 **COMANDOS DISPONIBLES**

**Información:**
• `.ping` - Comprueba la latencia del bot
• `.alive` - Muestra el estado del bot
• `.userinfo` - Información detallada de usuario
• `.sysinfo` - Información del sistema

**Utilidades:**
• `.guardarnota` - Guarda una nota
• `.nota` - Muestra una nota guardada
• `.purge` - Borra mensajes en masa
• `.wiki` - Busca en Wikipedia
• `.clima` - Muestra el clima de una ciuda

**Diversión:**
• `.dado` - Lanza un dado
• `.moneda` - Lanza una moneda

**Para más detalles de cada comando, usa** `.help [comando]`
"""
    await event.reply(help_text)

# Función principal
def main():
    print("🤖 Iniciando UserBot avanzado...")
    
    # Crear archivo de notas si no existe
    if not os.path.exists(NOTAS_FILE):
        with open(NOTAS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)
    
    print("✅ Sistema de notas inicializado")
    
    # Iniciar el cliente
    client.start()
    
    print("✅ Bot conectado a Telegram")
    print
