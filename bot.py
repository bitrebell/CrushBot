import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
from spotify_handler import SpotifyHandler

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Spotify handler
spotify_handler = SpotifyHandler(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    download_dir=os.getenv('DOWNLOAD_DIR', './downloads')
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎵 *Welcome to CrushBot Music Bot!* 🎵\n\n"
        "I can help you search and download music from Spotify.\n\n"
        "*Commands:*\n"
        "/start - Show this welcome message\n"
        "/search <song name> - Search for a song\n"
        "/help - Show help information\n\n"
        "Just send me a song name or Spotify link, and I'll handle the rest!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "*CrushBot Help* 🎵\n\n"
        "*How to use:*\n"
        "1. Send me a song name (e.g., 'Bohemian Rhapsody Queen')\n"
        "2. Use /search command (e.g., /search Shape of You)\n"
        "3. Send a Spotify track link\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/search <query> - Search for songs\n"
        "/help - This help message\n\n"
        "*Features:*\n"
        "✅ Search Spotify tracks\n"
        "✅ Download high-quality music\n"
        "✅ Get track information\n"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /search command."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a search query.\nExample: /search Imagine Dragons"
        )
        return

    query = ' '.join(context.args)
    await search_music(update, query)


async def search_music(update: Update, query: str) -> None:
    """Search for music on Spotify and display results."""
    await update.message.reply_text(f"🔍 Searching for: *{query}*...", parse_mode='Markdown')
    
    try:
        results = spotify_handler.search_tracks(query, limit=5)
        
        if not results:
            await update.message.reply_text(
                "❌ No results found. Please try a different search query."
            )
            return
        
        # Create inline keyboard with results
        keyboard = []
        message_text = "🎵 *Search Results:*\n\n"
        
        for idx, track in enumerate(results, 1):
            artist = track['artist']
            title = track['name']
            album = track['album']
            duration = track['duration']
            
            message_text += (
                f"{idx}. *{title}*\n"
                f"   Artist: {artist}\n"
                f"   Album: {album}\n"
                f"   Duration: {duration}\n\n"
            )
            
            # Add download button
            keyboard.append([
                InlineKeyboardButton(
                    f"⬇️ Download #{idx}",
                    callback_data=f"download_{track['id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(
            "❌ An error occurred while searching. Please try again later."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages (song names or Spotify links)."""
    text = update.message.text.strip()
    
    # Check if it's a Spotify link
    if 'spotify.com/track/' in text:
        await handle_spotify_link(update, text)
    else:
        # Treat as search query
        await search_music(update, text)


async def handle_spotify_link(update: Update, spotify_url: str) -> None:
    """Handle Spotify track links."""
    await update.message.reply_text("🎵 Processing Spotify link...")
    
    try:
        track_info = spotify_handler.get_track_info(spotify_url)
        
        if not track_info:
            await update.message.reply_text("❌ Invalid Spotify link.")
            return
        
        message_text = (
            f"🎵 *Track Found:*\n\n"
            f"*Title:* {track_info['name']}\n"
            f"*Artist:* {track_info['artist']}\n"
            f"*Album:* {track_info['album']}\n"
            f"*Duration:* {track_info['duration']}\n"
        )
        
        keyboard = [[
            InlineKeyboardButton(
                "⬇️ Download",
                callback_data=f"download_{track_info['id']}"
            )
        ]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Spotify link error: {e}")
        await update.message.reply_text("❌ Error processing Spotify link.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('download_'):
        track_id = query.data.replace('download_', '')
        await download_track(query, track_id)


async def download_track(query, track_id: str) -> None:
    """Download a track and send it to the user."""
    await query.edit_message_text("⬇️ Downloading... Please wait.")
    
    try:
        # Get track info
        track_info = spotify_handler.get_track_by_id(track_id)
        
        if not track_info:
            await query.edit_message_text("❌ Track not found.")
            return
        
        # Download track
        file_path = spotify_handler.download_track(track_id)
        
        if not file_path or not os.path.exists(file_path):
            await query.edit_message_text(
                "❌ Download failed. The track might not be available."
            )
            return
        
        # Send audio file
        await query.edit_message_text("📤 Uploading...")
        
        with open(file_path, 'rb') as audio:
            await query.message.reply_audio(
                audio=audio,
                title=track_info['name'],
                performer=track_info['artist'],
                duration=track_info['duration_seconds']
            )
        
        await query.edit_message_text("✅ Download complete!")
        
        # Clean up downloaded file
        try:
            os.remove(file_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        await query.edit_message_text(
            "❌ An error occurred during download. Please try again."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
