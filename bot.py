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
from pyrogram import Client
from pytgcalls import PyTgCalls
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

# Global Pyrogram client and PyTgCalls instance (will be initialized in main)
pyrogram_client = None
pytgcalls = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎵 *Welcome to CrushBot Music Bot!* 🎵\n\n"
        "I can play music in voice chats from Spotify!\n\n"
        "*Commands:*\n"
        "/start - Show this welcome message\n"
        "/search <song name> - Search for a song\n"
        "/play <song name> - Play song in voice chat\n"
        "/stop - Stop playback\n"
        "/help - Show help information\n\n"
        "Just send me a song name or Spotify link!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "*CrushBot Help* 🎵\n\n"
        "*How to use:*\n"
        "1. Add me to a group\n"
        "2. Start a voice chat\n"
        "3. Use /play <song name> to play music\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/search <query> - Search for songs\n"
        "/play <song name> - Play in voice chat\n"
        "/stop - Stop playback\n"
        "/help - This help message\n\n"
        "*Features:*\n"
        "✅ Search Spotify tracks\n"
        "✅ Play in voice chats\n"
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


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /play command to play a song in voice chat."""
    if not context.args:
        await update.message.reply_text(
            "Please provide a song name.\nExample: /play Bohemian Rhapsody"
        )
        return

    query = ' '.join(context.args)
    await update.message.reply_text(f"🔍 Searching for: *{query}*...", parse_mode='Markdown')
    
    try:
        # Search for the track
        results = spotify_handler.search_tracks(query, limit=1)
        
        if not results:
            await update.message.reply_text("❌ No results found. Please try a different search query.")
            return
        
        track = results[0]
        track_id = track['id']
        
        await update.message.reply_text("🎵 Preparing to play... Please wait.")
        
        # Get track info
        track_info = spotify_handler.get_track_by_id(track_id)
        
        if not track_info:
            await update.message.reply_text("❌ Track not found.")
            return
        
        # Download track temporarily for streaming
        file_path = await spotify_handler.download_track(track_id)
        
        if not file_path or not os.path.exists(file_path):
            await update.message.reply_text(
                "❌ Failed to prepare track. It might not be available."
            )
            return
        
        # Check if bot is in a voice chat
        chat_id = update.message.chat_id
        
        try:
            # Join voice chat and play
            await pytgcalls.play(
                chat_id,
                file_path
            )
            
            await update.message.reply_text(
                f"▶️ Now playing: *{track_info['name']}* by {track_info['artist']}",
                parse_mode='Markdown'
            )
        except Exception as vc_error:
            logger.error(f"Voice chat error: {vc_error}")
            await update.message.reply_text(
                "❌ Failed to play in voice chat. Make sure:\n"
                "1. There's an active voice chat\n"
                "2. I have permission to join"
            )
            # Clean up file
            try:
                os.remove(file_path)
            except Exception:
                pass
            
    except Exception as e:
        logger.error(f"Play command error: {e}")
        await update.message.reply_text(
            "❌ An error occurred. Please try again."
        )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stop command to stop playback."""
    chat_id = update.message.chat_id
    
    try:
        await pytgcalls.leave_call(chat_id)
        await update.message.reply_text("⏹️ Playback stopped and left voice chat.")
    except Exception as e:
        logger.error(f"Stop command error: {e}")
        await update.message.reply_text(
            "❌ I'm not currently in a voice chat or an error occurred."
        )


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
            
            # Add play button
            keyboard.append([
                InlineKeyboardButton(
                    f"▶️ Play #{idx}",
                    callback_data=f"play_{track['id']}"
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
                "▶️ Play",
                callback_data=f"play_{track_info['id']}"
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
    
    if query.data.startswith('play_'):
        track_id = query.data.replace('play_', '')
        await play_track(query, track_id)


async def play_track(query, track_id: str) -> None:
    """Play a track in voice chat."""
    await query.edit_message_text("🎵 Preparing to play... Please wait.")
    
    try:
        # Get track info
        track_info = spotify_handler.get_track_by_id(track_id)
        
        if not track_info:
            await query.edit_message_text("❌ Track not found.")
            return
        
        # Download track temporarily for streaming
        file_path = await spotify_handler.download_track(track_id)
        
        if not file_path or not os.path.exists(file_path):
            await query.edit_message_text(
                "❌ Failed to prepare track. It might not be available."
            )
            return
        
        # Check if bot is in a voice chat
        chat_id = query.message.chat_id
        
        try:
            # Join voice chat and play
            await pytgcalls.play(
                chat_id,
                file_path
            )
            
            await query.edit_message_text(
                f"▶️ Now playing: *{track_info['name']}* by {track_info['artist']}",
                parse_mode='Markdown'
            )
        except Exception as vc_error:
            logger.error(f"Voice chat error: {vc_error}")
            await query.edit_message_text(
                "❌ Failed to play in voice chat. Make sure:\n"
                "1. There's an active voice chat\n"
                "2. I have permission to join"
            )
            # Clean up file
            try:
                os.remove(file_path)
            except Exception:
                pass
            
    except Exception as e:
        logger.error(f"Play error: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again."
        )


def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    global pyrogram_client, pytgcalls
    
    # Get tokens from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    if not api_id or not api_hash:
        logger.error("API_ID and API_HASH are required for voice chat functionality!")
        logger.error("Get them from https://my.telegram.org/apps")
        return
    
    # Create Pyrogram client for voice chat
    pyrogram_client = Client(
        "crushbot_session",
        api_id=api_id,
        api_hash=api_hash,
        bot_token=token
    )
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Initialize PyTgCalls with Pyrogram client
    pytgcalls = PyTgCalls(pyrogram_client)
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("play", play_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start Pyrogram client and PyTgCalls
    logger.info("Starting Pyrogram client...")
    pyrogram_client.start()
    pytgcalls.start()
    
    # Start the bot
    logger.info("Bot is starting...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        # Stop Pyrogram client on exit
        pyrogram_client.stop()


if __name__ == '__main__':
    main()
