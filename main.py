"""
CrushBot - Advanced Telegram Userbot
Author: GitHub Copilot
Version: 1.0.0
"""

import os
import sys
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('userbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
SESSION_STRING = os.getenv("SESSION_STRING")

if not API_ID or not API_HASH:
    logger.error("API_ID and API_HASH are required!")
    sys.exit(1)

# Create the client
if SESSION_STRING:
    app = Client("userbot", session_string=SESSION_STRING)
else:
    app = Client("userbot", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)

# Store for message editing
message_store = {}

print(f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🤖 CrushBot Started 🤖                    ║
║                                                              ║
║                Advanced Telegram Userbot                     ║
║                     Version 1.0.0                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
""")

@app.on_message(filters.command("help", prefixes="."))
async def help_command(client: Client, message: Message):
    """Display help message with all available commands"""
    help_text = """
🤖 **CrushBot - Advanced Features**

**🔧 Basic Commands:**
`.help` - Show this help message
`.ping` - Check bot latency
`.info` - Get chat/user information
`.id` - Get user/chat ID

**📝 Text Commands:**
`.type <text>` - Typewriter effect
`.reverse <text>` - Reverse text
`.upper <text>` - Convert to uppercase
`.lower <text>` - Convert to lowercase
`.count <text>` - Count characters/words

**🎭 Fun Commands:**
`.dice` - Roll a dice
`.coin` - Flip a coin
`.8ball <question>` - Magic 8-ball
`.mock <text>` - Mock text (AlTeRnAtInG cAsE)
`.fancy <text>` - Fancy text formatting

**🖼️ Media Commands:**
`.sticker` - Convert photo to sticker
`.circle` - Make profile photo circular
`.blur <amount>` - Blur an image

**🌐 Utility Commands:**
`.weather <city>` - Get weather information
`.qr <text>` - Generate QR code
`.shorturl <url>` - Shorten URL
`.ytdl <url>` - Download YouTube video info
`.speed` - Internet speed test

**🔨 System Commands:**
`.sys` - System information
`.uptime` - Bot uptime
`.restart` - Restart the bot
`.logs` - Get recent logs

**⚡ Advanced Commands:**
`.auto_react` - Auto react to messages
`.spam <count> <text>` - Spam messages (use carefully)
`.purge` - Delete messages in bulk
`.translate <lang> <text>` - Translate text

Use these commands with `.` prefix in any chat!
    """
    await message.edit_text(help_text, disable_web_page_preview=True)

@app.on_message(filters.command("ping", prefixes="."))
async def ping_command(client: Client, message: Message):
    """Check bot latency"""
    import time
    start_time = time.time()
    msg = await message.edit_text("🏓 Pinging...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⚡ Latency: `{latency}ms`")

@app.on_message(filters.command("restart", prefixes="."))
async def restart_command(client: Client, message: Message):
    """Restart the bot"""
    await message.edit_text("🔄 **Restarting CrushBot...**")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Load all plugins
async def load_plugins():
    """Load all plugin files"""
    plugin_dir = "plugins"
    if os.path.exists(plugin_dir):
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_name = filename[:-3]
                try:
                    __import__(f"plugins.{plugin_name}")
                    logger.info(f"✅ Loaded plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")

async def main():
    """Main function to start the bot"""
    try:
        await load_plugins()
        await app.start()
        logger.info("🚀 CrushBot is now running!")
        print(f"{Fore.GREEN}✅ Bot started successfully!{Style.RESET_ALL}")
        await asyncio.Event().wait()  # Keep the bot running
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
