"""
Advanced commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import aiohttp
from pyrogram.errors import FloodWait
import time

# Global variables for advanced features
auto_react_enabled = False
auto_react_chats = set()

@Client.on_message(filters.command("spam", prefixes="."))
async def spam_command(client: Client, message: Message):
    """Spam messages (use carefully!)"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.spam <count> <text>`\n⚠️ **Warning:** Use responsibly!")
        return
    
    try:
        count = int(message.command[1])
        if count > 50:
            await message.edit_text("❌ Maximum 50 messages allowed")
            return
        
        text = message.text.split(None, 2)[2]
        
        await message.delete()
        
        for i in range(count):
            try:
                await client.send_message(message.chat.id, text)
                await asyncio.sleep(0.5)  # Delay to avoid flood limits
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(message.chat.id, text)
            except Exception:
                break
                
    except ValueError:
        await message.edit_text("❌ Count must be a number")
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("purge", prefixes="."))
async def purge_messages(client: Client, message: Message):
    """Delete messages in bulk"""
    if not message.reply_to_message:
        await message.edit_text("❌ Reply to a message to purge from that point")
        return
    
    try:
        await message.edit_text("🗑️ Purging messages...")
        
        start_id = message.reply_to_message.id
        end_id = message.id
        
        deleted_count = 0
        
        # Get messages to delete
        messages_to_delete = []
        async for msg in client.get_chat_history(message.chat.id, limit=None):
            if start_id <= msg.id <= end_id:
                messages_to_delete.append(msg.id)
            if msg.id < start_id:
                break
        
        # Delete in chunks
        chunk_size = 100
        for i in range(0, len(messages_to_delete), chunk_size):
            chunk = messages_to_delete[i:i + chunk_size]
            try:
                await client.delete_messages(message.chat.id, chunk)
                deleted_count += len(chunk)
                await asyncio.sleep(1)
            except Exception:
                pass
        
        # Send result message and delete it after a few seconds
        result_msg = await client.send_message(
            message.chat.id, 
            f"🗑️ **Purged {deleted_count} messages**"
        )
        await asyncio.sleep(3)
        await result_msg.delete()
        
    except Exception as e:
        await message.edit_text(f"❌ Error purging: {str(e)}")

@Client.on_message(filters.command("auto_react", prefixes="."))
async def auto_react_toggle(client: Client, message: Message):
    """Toggle auto react to messages"""
    global auto_react_enabled, auto_react_chats
    
    if len(message.command) == 1:
        auto_react_enabled = not auto_react_enabled
        status = "enabled" if auto_react_enabled else "disabled"
        await message.edit_text(f"🔄 **Auto React:** {status}")
    elif message.command[1].lower() == "add":
        auto_react_chats.add(message.chat.id)
        await message.edit_text("✅ **Auto React enabled for this chat**")
    elif message.command[1].lower() == "remove":
        auto_react_chats.discard(message.chat.id)
        await message.edit_text("❌ **Auto React disabled for this chat**")
    else:
        await message.edit_text("❌ Usage: `.auto_react` or `.auto_react add/remove`")

@Client.on_message(filters.all & ~filters.me)
async def auto_react_handler(client: Client, message: Message):
    """Auto react to messages"""
    global auto_react_enabled, auto_react_chats
    
    if auto_react_enabled or message.chat.id in auto_react_chats:
        try:
            reactions = ["❤️", "👍", "😂", "😮", "😢", "🔥", "👎"]
            reaction = random.choice(reactions)
            await message.react(reaction)
        except Exception:
            pass

@Client.on_message(filters.command("translate", prefixes="."))
async def translate_text(client: Client, message: Message):
    """Translate text"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.translate <language> <text>`\nExample: `.translate es Hello World`")
        return
    
    target_lang = message.command[1]
    text = message.text.split(None, 2)[2]
    
    try:
        await message.edit_text("🌍 Translating...")
        
        # Using Google Translate API (free)
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    translated = result[0][0][0]
                    
                    translate_text = f"""
🌍 **Translation**

**Original:** `{text}`
**Translated ({target_lang}):** `{translated}`
                    """
                    
                    await message.edit_text(translate_text.strip())
                else:
                    await message.edit_text("❌ Translation failed")
                    
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("youtube", prefixes="."))
async def youtube_search(client: Client, message: Message):
    """Search YouTube videos"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.youtube <search query>`")
        return
    
    query = message.text.split(None, 1)[1]
    
    try:
        await message.edit_text("🔍 Searching YouTube...")
        
        # Using YouTube search (simplified)
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        youtube_text = f"""
📺 **YouTube Search**

**Query:** `{query}`
**Search URL:** {search_url}

Use the URL above to see search results on YouTube.
        """
        
        await message.edit_text(youtube_text.strip())
        
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("ascii", prefixes="."))
async def ascii_art(client: Client, message: Message):
    """Convert text to ASCII art"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.ascii <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    
    # Simple ASCII art conversion
    ascii_chars = {
        'A': ['  █  ', ' █ █ ', '█████', '█   █', '█   █'],
        'B': ['████ ', '█   █', '████ ', '█   █', '████ '],
        'C': [' ████', '█    ', '█    ', '█    ', ' ████'],
        'H': ['█   █', '█   █', '█████', '█   █', '█   █'],
        'I': ['█████', '  █  ', '  █  ', '  █  ', '█████'],
        'L': ['█    ', '█    ', '█    ', '█    ', '█████'],
        'O': [' ███ ', '█   █', '█   █', '█   █', ' ███ '],
        ' ': ['     ', '     ', '     ', '     ', '     ']
    }
    
    if len(text) > 10:
        await message.edit_text("❌ Text too long (max 10 characters)")
        return
    
    try:
        lines = ['', '', '', '', '']
        
        for char in text.upper():
            if char in ascii_chars:
                for i in range(5):
                    lines[i] += ascii_chars[char][i] + ' '
            else:
                for i in range(5):
                    lines[i] += '█████ '
        
        ascii_art = f"```\n{chr(10).join(lines)}\n```"
        await message.edit_text(f"🎨 **ASCII Art:**\n\n{ascii_art}")
        
    except Exception as e:
        await message.edit_text(f"❌ Error creating ASCII art: {str(e)}")

@Client.on_message(filters.command("math", prefixes="."))
async def advanced_math(client: Client, message: Message):
    """Advanced mathematical operations"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.math <operation> <numbers>`\nOperations: sqrt, pow, sin, cos, tan, log")
        return
    
    try:
        import math
        
        operation = message.command[1].lower()
        
        if operation == "sqrt" and len(message.command) >= 3:
            num = float(message.command[2])
            result = math.sqrt(num)
            await message.edit_text(f"📐 **√{num}** = `{result:.6f}`")
            
        elif operation == "pow" and len(message.command) >= 4:
            base = float(message.command[2])
            exp = float(message.command[3])
            result = math.pow(base, exp)
            await message.edit_text(f"📐 **{base}^{exp}** = `{result:.6f}`")
            
        elif operation in ["sin", "cos", "tan"] and len(message.command) >= 3:
            angle = float(message.command[2])
            radians = math.radians(angle)
            
            if operation == "sin":
                result = math.sin(radians)
            elif operation == "cos":
                result = math.cos(radians)
            else:  # tan
                result = math.tan(radians)
                
            await message.edit_text(f"📐 **{operation}({angle}°)** = `{result:.6f}`")
            
        elif operation == "log" and len(message.command) >= 3:
            num = float(message.command[2])
            if num <= 0:
                await message.edit_text("❌ Logarithm undefined for non-positive numbers")
                return
            result = math.log10(num)
            await message.edit_text(f"📐 **log₁₀({num})** = `{result:.6f}`")
            
        else:
            await message.edit_text("❌ Invalid operation or missing parameters")
            
    except ValueError:
        await message.edit_text("❌ Invalid number format")
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")
