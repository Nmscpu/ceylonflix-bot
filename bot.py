import os
import logging
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

# ඔබගේ ලබා දී ඇති නිවැරදි දත්ත
API_ID = int(os.environ.get("API_ID", "34466015"))
API_HASH = os.environ.get("API_HASH", "4118dca3ee2cbad40478f9cefe2375bf")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9141486229:AAHGBUVpPI_r60TF3NGUcAI2YGS5DgQTV34")
PORT = int(os.environ.get("PORT", 8080))

app = Client("tg_stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    return web.Response(text="CeylonFlix Telegram Stream Bot is Running!")

@routes.get("/watch/{file_id}")
async def stream_handler(request):
    file_id = request.match_info["file_id"]
    return web.Response(text=f"Streaming file ID: {file_id}")

async def web_server():
    server = web.Application()
    server.add_routes(routes)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

@app.on_message(filters.document | filters.video | filters.audio)
async def handle_file(client: Client, message: Message):
    media = message.document or message.video or message.audio
    file_id = media.file_id
    file_name = getattr(media, "file_name", "video.mp4")
    
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8080")
    direct_link = f"{base_url}/watch/{file_id}"
    
    await message.reply_text(
        f"✅ **Movie File Received!**\n\n"
        f"📁 **Name:** `{file_name}`\n"
        f"🔗 **Direct Link / Stream Link:**\n`{direct_link}`"
    )

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(web_server())
    app.run()
