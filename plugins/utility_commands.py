"""
Utility commands plugin for CrushBot
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import asyncio
import qrcode
import io
import os
from datetime import datetime
import speedtest

@Client.on_message(filters.command("weather", prefixes="."))
async def weather_command(client: Client, message: Message):
    """Get weather information"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.weather <city>`")
        return
    
    city = message.text.split(None, 1)[1]
    api_key = os.getenv("WEATHER_API_KEY")
    
    if not api_key:
        await message.edit_text("❌ Weather API key not configured")
        return
    
    try:
        await message.edit_text("🌤️ Getting weather data...")
        
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    temp = data['main']['temp']
                    feels_like = data['main']['feels_like']
                    humidity = data['main']['humidity']
                    pressure = data['main']['pressure']
                    description = data['weather'][0]['description'].title()
                    wind_speed = data['wind']['speed']
                    
                    weather_text = f"""
🌤️ **Weather in {city.title()}**

**Temperature:** `{temp}°C` (feels like `{feels_like}°C`)
**Condition:** `{description}`
**Humidity:** `{humidity}%`
**Pressure:** `{pressure} hPa`
**Wind Speed:** `{wind_speed} m/s`
                    """
                    
                    await message.edit_text(weather_text.strip())
                else:
                    await message.edit_text("❌ City not found")
    except Exception as e:
        await message.edit_text(f"❌ Error fetching weather: {str(e)}")

@Client.on_message(filters.command("qr", prefixes="."))
async def qr_generator(client: Client, message: Message):
    """Generate QR code"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.qr <text>`")
        return
    
    text = message.text.split(None, 1)[1]
    
    try:
        await message.edit_text("📱 Generating QR code...")
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        
        # Send photo
        await message.delete()
        await client.send_photo(
            chat_id=message.chat.id,
            photo=bio,
            caption=f"📱 **QR Code for:**\n`{text}`"
        )
        
    except Exception as e:
        await message.edit_text(f"❌ Error generating QR code: {str(e)}")

@Client.on_message(filters.command("shorturl", prefixes="."))
async def shorten_url(client: Client, message: Message):
    """Shorten URL using is.gd"""
    if len(message.command) < 2:
        await message.edit_text("❌ Usage: `.shorturl <url>`")
        return
    
    url = message.command[1]
    
    try:
        await message.edit_text("🔗 Shortening URL...")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"https://is.gd/create.php?format=simple&url={url}"
            async with session.get(api_url) as response:
                if response.status == 200:
                    short_url = await response.text()
                    if short_url.startswith("http"):
                        await message.edit_text(f"🔗 **Original:** {url}\n\n🔗 **Shortened:** {short_url}")
                    else:
                        await message.edit_text(f"❌ Error: {short_url}")
                else:
                    await message.edit_text("❌ Failed to shorten URL")
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("speed", prefixes="."))
async def speed_test(client: Client, message: Message):
    """Test internet speed"""
    try:
        await message.edit_text("🚀 Testing internet speed...")
        
        # This might take a while, so we'll do it in a separate thread
        def run_speedtest():
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000      # Convert to Mbps
            ping = st.results.ping
            
            return download_speed, upload_speed, ping
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        download, upload, ping = await loop.run_in_executor(None, run_speedtest)
        
        speed_text = f"""
🚀 **Internet Speed Test**

**Download:** `{download:.2f} Mbps`
**Upload:** `{upload:.2f} Mbps`
**Ping:** `{ping:.2f} ms`

**Server:** Speedtest.net
        """
        
        await message.edit_text(speed_text.strip())
        
    except Exception as e:
        await message.edit_text(f"❌ Error testing speed: {str(e)}")

@Client.on_message(filters.command("time", prefixes="."))
async def current_time(client: Client, message: Message):
    """Get current time and date"""
    now = datetime.now()
    
    time_text = f"""
🕐 **Current Time**

**Date:** `{now.strftime('%Y-%m-%d')}`
**Time:** `{now.strftime('%H:%M:%S')}`
**Timezone:** `{now.strftime('%Z')}`
**Weekday:** `{now.strftime('%A')}`
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
        # Basic security check
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            await message.edit_text("❌ Invalid characters in expression")
            return
        
        result = eval(expression)
        await message.edit_text(f"🧮 **Calculator**\n\n`{expression}` = `{result}`")
        
    except ZeroDivisionError:
        await message.edit_text("❌ Error: Division by zero")
    except Exception as e:
        await message.edit_text(f"❌ Error: Invalid expression")

@Client.on_message(filters.command("base64", prefixes="."))
async def base64_encode_decode(client: Client, message: Message):
    """Encode/decode base64"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.base64 <encode|decode> <text>`")
        return
    
    action = message.command[1].lower()
    text = message.text.split(None, 2)[2]
    
    try:
        import base64
        
        if action == "encode":
            encoded = base64.b64encode(text.encode()).decode()
            await message.edit_text(f"🔐 **Base64 Encoded:**\n`{encoded}`")
        elif action == "decode":
            decoded = base64.b64decode(text.encode()).decode()
            await message.edit_text(f"🔓 **Base64 Decoded:**\n`{decoded}`")
        else:
            await message.edit_text("❌ Use 'encode' or 'decode'")
            
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("hash", prefixes="."))
async def hash_text(client: Client, message: Message):
    """Generate hash of text"""
    if len(message.command) < 3:
        await message.edit_text("❌ Usage: `.hash <md5|sha1|sha256> <text>`")
        return
    
    hash_type = message.command[1].lower()
    text = message.text.split(None, 2)[2]
    
    try:
        import hashlib
        
        if hash_type == "md5":
            hash_obj = hashlib.md5(text.encode())
        elif hash_type == "sha1":
            hash_obj = hashlib.sha1(text.encode())
        elif hash_type == "sha256":
            hash_obj = hashlib.sha256(text.encode())
        else:
            await message.edit_text("❌ Supported: md5, sha1, sha256")
            return
        
        hash_value = hash_obj.hexdigest()
        await message.edit_text(f"🔐 **{hash_type.upper()} Hash:**\n`{hash_value}`")
        
    except Exception as e:
        await message.edit_text(f"❌ Error: {str(e)}")
