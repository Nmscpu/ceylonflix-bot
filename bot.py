import os
import asyncio
from pyrogram import Client, filters
from aiohttp import web

# Environment variables මඟින් ලබාගැනීම
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram Bot Client එක ආරම්භ කිරීම
app = Client(
    "ceylonflix_bot",
    api_id=int(API_ID) if API_ID else 0,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ඩවුන්ලෝඩ් හෝ ස්ට්‍රීම් ලින්ක් එක ක්‍රියාත්මක කරන Handler එක
async def download_handler(request):
    file_id = request.match_info.get("file_id")
    try:
        # Pyrogram හරහා Telegram සර්වර් එකෙන් file object එක ලබා ගැනීම
        file_info = await app.get_file(file_id)
        file_path = file_info.file_path
        telegram_file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # පරිශීලකයාට කෙලින්ම Telegram සර්වර් එකෙන් ෆයිල් එක ලබා දීමට Redirect කිරීම
        raise web.HTTPFound(telegram_file_url)
    except Exception as e:
        return web.Response(text=f"Error fetching file: {str(e)}", status=500)

# ප්‍රධාන රූට් එක
async def handle(request):
    return web.Response(text="CeylonFlix Telegram Bot is Alive and Running!")

# වෙබ් සර්වර් එක සැකසීම
async def web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    server.router.add_get("/download/{file_id}", download_handler)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ස්ටාර්ට් කමාන්ඩ් එක
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "👋 **স্বalvathkarani!** මෙი CeylonFlix මූවි සයිට් එකේ Direct Download & Streaming Bot එකයි.\n\n"
        "ඔබට අවශ්‍ය මූවි ෆයිල් එක (Video file එක) මට මෙතැනට ෆෝවර්ඩ් කරන්න හෝ අප්ලෝඩ් කරන්න. "
        "මම ඔබට ක්ෂණිකව Direct Download Link එක ලබා දෙන්නම්! 🎬"
    )

# මූවි ෆයිල් එකක් ලැබුණු විට ලින්ක් එක ලබා දීම
@app.on_message(filters.video | filters.document)
async def file_handler(client, message):
    media = message.video or message.document
    file_id = media.file_id
    file_name = media.file_name if hasattr(media, "file_name") else "video_file.mp4"
    file_size = round(media.file_size / (1024 * 1024), 2) if hasattr(media, "file_size") else 0
    
    render_external_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8080")
    direct_link = f"{render_external_url}/download/{file_id}"
    
    reply_text = (
        "✅ **File Received Successfully!**\n\n"
        f"📁 **Name:** `{file_name}`\n"
        f"📊 **Size:** `{file_size} MB`\n\n"
        f"🔗 **Direct Download / Stream Link:**\n`{direct_link}`"
    )
    
    await message.reply_text(reply_text, disable_web_page_preview=True)

# බොට් සහ වෙබ් සර්වර් එක එකට රන් කිරීම සඳහා
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(web_server())
    app.run()
