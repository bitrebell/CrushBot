"""
Basic commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import sys
import os

# Add parent directory to path for imports


@Client.on_message(filters.command("id", prefixes="."))
async def get_id(client: Client, message: Message):
    """Get user/chat ID information"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.id
    
    text = f"""
🆔 **ID Information**

**User ID:** `{user_id}`
**Chat ID:** `{chat_id}`
**Message ID:** `{message_id}`
    """
    
    if message.reply_to_message:
        replied_user_id = message.reply_to_message.from_user.id
        replied_message_id = message.reply_to_message.id
        text += f"\n**Replied User ID:** `{replied_user_id}`"
        text += f"\n**Replied Message ID:** `{replied_message_id}`"
    
    await message.edit_text(text.strip())

@Client.on_message(filters.command("info", prefixes="."))
async def get_info(client: Client, message: Message):
    """Get detailed information about user/chat"""
    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user
        
        chat = message.chat
        
        text = f"""
ℹ️ **Information**

**User:**
• Name: `{user.first_name or 'N/A'} {user.last_name or ''}`
• Username: `@{user.username or 'None'}`
• ID: `{user.id}`
• Is Bot: `{user.is_bot}`
• Is Premium: `{getattr(user, 'is_premium', 'Unknown')}`

**Chat:**
• Title: `{getattr(chat, 'title', 'Private Chat')}`
• Type: `{chat.type}`
• ID: `{chat.id}`
• Members Count: `{getattr(chat, 'members_count', 'Unknown')}`
        """
        
        await message.edit_text(text.strip())
    except Exception as e:
        await message.edit_text(f"❌ Error getting info: {str(e)}")

@Client.on_message(filters.command("sys", prefixes="."))
async def system_info(client: Client, message: Message):
    """Get system information"""
    await message.edit_text("🔄 Getting system information...")
    info = get_system_info()
    await message.edit_text(info)

@Client.on_message(filters.command("uptime", prefixes="."))
async def uptime_command(client: Client, message: Message):
    """Get bot uptime"""
    uptime = get_bot_uptime()
    await message.edit_text(f"⏰ **Bot Uptime:** `{uptime}`")

@Client.on_message(filters.command("logs", prefixes="."))
async def get_logs(client: Client, message: Message):
    """Get recent bot logs"""
    try:
        if os.path.exists("userbot.log"):
            with open("userbot.log", "r") as f:
                logs = f.readlines()
            
            # Get last 20 lines
            recent_logs = "".join(logs[-20:])
            
            if len(recent_logs) > 4000:
                recent_logs = recent_logs[-4000:]
            
            await message.edit_text(f"📋 **Recent Logs:**\n\n```\n{recent_logs}\n```")
        else:
            await message.edit_text("❌ No log file found")
    except Exception as e:
        await message.edit_text(f"❌ Error reading logs: {str(e)}")

@Client.on_message(filters.command("count", prefixes="."))
async def count_text(client: Client, message: Message):
    """Count characters and words in text"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.count <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    stats = get_text_stats(text)
    await message.edit_text(stats)

@Client.on_message(filters.command("type", prefixes="."))
async def typewriter_effect(client: Client, message: Message):
    """Create typewriter effect"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.type <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    await typing_effect(message, text, delay=0.05)
