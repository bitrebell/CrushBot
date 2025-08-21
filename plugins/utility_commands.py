"""
Utility commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import qrcode
import io
import base64
import hashlib
import speedtest
from datetime import datetime
import asyncio

@Client.on_message(filters.command("qr", prefixes="."))
async def qr_code_generator(client: Client, message: Message):
    """Generate QR code"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.qr <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    
    try:
        await message.edit_text("📱 Generating QR code...")
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, 'PNG')
        output.seek(0)
        
        # Send QR code
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=output,
            caption=f"📱 **QR Code for:** `{text}`"
        )
        
    except Exception as e:
        await message.edit_text(f"❌ Error generating QR code: {str(e)}")

@Client.on_message(filters.command("speed", prefixes="."))
async def speed_test(client: Client, message: Message):
    """Internet speed test"""
    try:
        await message.edit_text("🌐 Running speed test...")
        
        st = speedtest.Speedtest()
        st.get_best_server()
        
        await message.edit_text("�� Testing download speed...")
        download_speed = st.download() / 1024 / 1024  # Convert to Mbps
        
        await message.edit_text("📤 Testing upload speed...")
        upload_speed = st.upload() / 1024 / 1024  # Convert to Mbps
        
        await message.edit_text("🏓 Testing ping...")
        ping = st.results.ping
        
        result = f"""
🌐 **Speed Test Results**

📥 **Download:** `{download_speed:.2f} Mbps`
📤 **Upload:** `{upload_speed:.2f} Mbps`
🏓 **Ping:** `{ping:.2f} ms`

**Server:** `{st.results.server['sponsor']} - {st.results.server['name']}`
**Location:** `{st.results.server['country']}`
        """
        
        await message.edit_text(result.strip())
        
    except Exception as e:
        await message.edit_text(f"❌ Error running speed test: {str(e)}")

@Client.on_message(filters.command("time", prefixes="."))
async def current_time(client: Client, message: Message):
    """Get current time and date"""
    now = datetime.now()
    
    time_text = f"""
🕐 **Current Time & Date**

**Date:** `{now.strftime('%A, %B %d, %Y')}`
**Time:** `{now.strftime('%I:%M:%S %p')}`
**24H Format:** `{now.strftime('%H:%M:%S')}`
**Timezone:** `{now.strftime('%Z')}`

**Unix Timestamp:** `{int(now.timestamp())}`
    """
    
    await message.edit_text(time_text.strip())

@Client.on_message(filters.command("calc", prefixes="."))
async def calculator(client: Client, message: Message):
    """Simple calculator"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.calc <expression>`\nExample: `.calc 2 + 2`")
        return
    
    expression = message.text.split(None, 1)[1]
    
    try:
        # Replace common symbols
        expression = expression.replace('x', '*').replace('÷', '/')
        
        # Evaluate safely (only allow basic math operations)
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            await message.edit_text("❌ Invalid characters in expression")
            return
        
        result = eval(expression)
        await message.edit_text(f"🧮 **Calculator**\n\n`{expression}` = **`{result}`**")
        
    except ZeroDivisionError:
        await message.edit_text("❌ Error: Division by zero")
    except Exception as e:
        await message.edit_text(f"❌ Error: Invalid expression")

@Client.on_message(filters.command("base64", prefixes="."))
async def base64_operations(client: Client, message: Message):
    """Base64 encode/decode"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.base64 <encode/decode> <text>`")
        return
    
    operation = message.command[1].lower()
    text = message.text.split(None, 2)[2]
    
    try:
        if operation == "encode":
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            await message.edit_text(f"🔐 **Base64 Encoded:**\n\n`{encoded}`")
        elif operation == "decode":
            decoded = base64.b64decode(text.encode('utf-8')).decode('utf-8')
            await message.edit_text(f"🔓 **Base64 Decoded:**\n\n`{decoded}`")
        else:
            await message.edit_text("❌ Use 'encode' or 'decode'")
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("hash", prefixes="."))
async def hash_generator(client: Client, message: Message):
    """Generate hash of text"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.hash <md5/sha1/sha256> <text>`")
        return
    
    hash_type = message.command[1].lower()
    text = message.text.split(None, 2)[2]
    
    try:
        if hash_type == "md5":
            hash_obj = hashlib.md5(text.encode('utf-8'))
        elif hash_type == "sha1":
            hash_obj = hashlib.sha1(text.encode('utf-8'))
        elif hash_type == "sha256":
            hash_obj = hashlib.sha256(text.encode('utf-8'))
        else:
            await message.edit_text("❌ Supported: md5, sha1, sha256")
            return
        
        hash_value = hash_obj.hexdigest()
        
        result = f"""
🔐 **Hash Generator**

**Algorithm:** `{hash_type.upper()}`
**Text:** `{text}`
**Hash:** `{hash_value}`
        """
        
        await message.edit_text(result.strip())
        
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("shorturl", prefixes="."))
async def url_shortener(client: Client, message: Message):
    """Shorten URL using a free service"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.shorturl <url>`")
        return
    
    url = message.text.split(None, 1)[1]
    
    try:
        await message.edit_text("🔗 Shortening URL...")
        
        # Using is.gd free URL shortener
        api_url = "https://is.gd/create.php"
        params = {
            'format': 'simple',
            'url': url
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    short_url = await response.text()
                    
                    result = f"""
🔗 **URL Shortened**

**Original:** `{url}`
**Shortened:** `{short_url}`
                    """
                    
                    await message.edit_text(result.strip())
                else:
                    await message.edit_text("❌ Failed to shorten URL")
                    
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

