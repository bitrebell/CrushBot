import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from downloader import download_video, download_audio

# Load environment variables
load_dotenv()

# Bot credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot
app = Client(
    "youtube_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store user download choices
user_downloads = {}


@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    welcome_text = (
        "👋 **Welcome to YouTube Downloader Bot!**\n\n"
        "Send me a YouTube link and I'll help you download it as:\n"
        "🎵 **Audio** (MP3)\n"
        "🎬 **Video** (MP4)\n\n"
        "Just send the link and choose your preferred format!"
    )
    await message.reply_text(welcome_text)


@app.on_message(filters.command("help"))
async def help_command(client, message):
    """Handle /help command"""
    help_text = (
        "**How to use this bot:**\n\n"
        "1️⃣ Send a YouTube video link\n"
        "2️⃣ Choose between Audio or Video format\n"
        "3️⃣ Wait for the download to complete\n"
        "4️⃣ Receive your file!\n\n"
        "**Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "**Supported formats:**\n"
        "🎵 Audio: MP3\n"
        "🎬 Video: MP4 (Best quality)"
    )
    await message.reply_text(help_text)


@app.on_message(filters.regex(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"))
async def handle_youtube_link(client, message):
    """Handle YouTube links"""
    url = message.text.strip()
    user_downloads[message.from_user.id] = url
    
    # Create inline keyboard with download options
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Audio (MP3)", callback_data="download_audio"),
            InlineKeyboardButton("🎬 Video (MP4)", callback_data="download_video")
        ]
    ])
    
    await message.reply_text(
        "**Choose download format:**\n\n"
        f"Link: `{url}`",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("^download_"))
async def handle_download_callback(client, callback_query):
    """Handle download button callbacks"""
    user_id = callback_query.from_user.id
    
    # Check if user has a saved URL
    if user_id not in user_downloads:
        await callback_query.answer("⚠️ Please send a YouTube link first!", show_alert=True)
        return
    
    url = user_downloads[user_id]
    download_type = callback_query.data.split("_")[1]  # 'audio' or 'video'
    
    # Answer callback query
    await callback_query.answer(f"Downloading {download_type}...")
    
    # Send processing message
    status_msg = await callback_query.message.reply_text(
        f"⏳ **Downloading {download_type}...**\n\n"
        "Please wait, this may take a few moments."
    )
    
    try:
        if download_type == "audio":
            file_path, title = await download_audio(url, status_msg)
            
            # Upload audio file
            await status_msg.edit_text("📤 **Uploading audio...**")
            await callback_query.message.reply_audio(
                audio=file_path,
                title=title,
                caption=f"🎵 **{title}**\n\nDownloaded by @{client.me.username}"
            )
            
        else:  # video
            file_path, title = await download_video(url, status_msg)
            
            # Upload video file
            await status_msg.edit_text("📤 **Uploading video...**")
            await callback_query.message.reply_video(
                video=file_path,
                caption=f"🎬 **{title}**\n\nDownloaded by @{client.me.username}",
                supports_streaming=True
            )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await status_msg.edit_text("✅ **Download complete!**")
        
        # Remove user's URL from cache
        if user_id in user_downloads:
            del user_downloads[user_id]
            
    except Exception as e:
        error_message = str(e)
        await status_msg.edit_text(
            f"❌ **Download failed!**\n\n"
            f"Error: `{error_message}`\n\n"
            "Please try again with a different link or format."
        )
        print(f"Error downloading {download_type}: {error_message}")


if __name__ == "__main__":
    print("🤖 Bot is starting...")
    app.run()
