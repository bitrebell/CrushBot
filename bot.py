"""
CrushBot - Personal Assistant Telegram Bot
A bot that monitors messages, forwards them to the owner, and sends offline notifications.
"""
import logging
import asyncio
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from config import Config, Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crushbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CrushBot:
    """Personal Assistant Telegram Bot"""
    
    def __init__(self):
        """Initialize the bot"""
        # Validate configuration
        if not Config.validate():
            missing = [var for var in Config.get_required_vars() 
                      if not getattr(Config, var, None)]
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # Initialize settings
        self.settings = Settings()
        
        # Initialize Pyrogram client
        self.app = Client(
            "crushbot_session",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )
        
        # Register handlers
        self._register_handlers()
        
        logger.info("CrushBot initialized successfully")
    
    def _register_handlers(self):
        """Register message and command handlers"""
        
        # Command handlers
        @self.app.on_message(filters.command("start") & filters.private & filters.user(Config.OWNER_ID))
        async def start_command(client, message: Message):
            await self.handle_start(message)
        
        @self.app.on_message(filters.command("enable") & filters.private & filters.user(Config.OWNER_ID))
        async def enable_command(client, message: Message):
            await self.handle_enable(message)
        
        @self.app.on_message(filters.command("disable") & filters.private & filters.user(Config.OWNER_ID))
        async def disable_command(client, message: Message):
            await self.handle_disable(message)
        
        @self.app.on_message(filters.command("status") & filters.private & filters.user(Config.OWNER_ID))
        async def status_command(client, message: Message):
            await self.handle_status(message)
        
        @self.app.on_message(filters.command("settings") & filters.private & filters.user(Config.OWNER_ID))
        async def settings_command(client, message: Message):
            await self.handle_settings(message)
        
        @self.app.on_message(filters.command("setoffline") & filters.private & filters.user(Config.OWNER_ID))
        async def setoffline_command(client, message: Message):
            await self.handle_set_offline_message(message)
        
        @self.app.on_message(filters.command("help") & filters.private & filters.user(Config.OWNER_ID))
        async def help_command(client, message: Message):
            await self.handle_help(message)
        
        # Incoming message handler (for non-owner messages)
        @self.app.on_message(filters.private & ~filters.user(Config.OWNER_ID) & ~filters.bot)
        async def incoming_private_message(client, message: Message):
            await self.handle_incoming_message(message)
        
        # Group message handler (mentions and direct interactions)
        @self.app.on_message(filters.group & ~filters.bot)
        async def group_message(client, message: Message):
            await self.handle_group_message(message)
    
    async def handle_start(self, message: Message):
        """Handle /start command"""
        try:
            welcome_text = (
                "👋 **Welcome to CrushBot!**\n\n"
                "Your personal assistant bot is ready to help you.\n\n"
                "**Features:**\n"
                "• Forward messages when you're offline\n"
                "• Send offline notifications\n"
                "• Alert you of direct messages\n"
                "• Customizable settings\n\n"
                "Use /help to see all available commands."
            )
            await message.reply_text(welcome_text)
            logger.info(f"Start command from owner (ID: {message.from_user.id})")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
    
    async def handle_enable(self, message: Message):
        """Enable the bot"""
        try:
            if self.settings.enable():
                await message.reply_text("✅ **Bot Enabled**\n\nI'm now active and will handle messages.")
                logger.info("Bot enabled by owner")
            else:
                await message.reply_text("❌ Failed to enable bot. Check logs for details.")
        except Exception as e:
            logger.error(f"Error enabling bot: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_disable(self, message: Message):
        """Disable the bot"""
        try:
            if self.settings.disable():
                await message.reply_text("🛑 **Bot Disabled**\n\nI won't send notifications or forward messages until re-enabled.")
                logger.info("Bot disabled by owner")
            else:
                await message.reply_text("❌ Failed to disable bot. Check logs for details.")
        except Exception as e:
            logger.error(f"Error disabling bot: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_status(self, message: Message):
        """Show bot status"""
        try:
            status = "🟢 **Enabled**" if self.settings.is_enabled() else "🔴 **Disabled**"
            settings_info = (
                f"**CrushBot Status**\n\n"
                f"Status: {status}\n"
                f"Offline Notifications: {'✅' if self.settings.get('offline_notification') else '❌'}\n"
                f"Forward Messages: {'✅' if self.settings.get('forward_messages') else '❌'}\n"
                f"Direct Message Alerts: {'✅' if self.settings.get('direct_message_alerts') else '❌'}\n\n"
                f"Use /settings to see all configuration options."
            )
            await message.reply_text(settings_info)
        except Exception as e:
            logger.error(f"Error showing status: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_settings(self, message: Message):
        """Show all settings"""
        try:
            settings_text = "⚙️ **Current Settings:**\n\n"
            for key, value in self.settings.settings.items():
                if key == "offline_message":
                    settings_text += f"**{key}:**\n`{value}`\n\n"
                else:
                    settings_text += f"**{key}:** `{value}`\n"
            
            settings_text += "\n**Available Commands:**\n"
            settings_text += "/enable - Enable bot\n"
            settings_text += "/disable - Disable bot\n"
            settings_text += "/setoffline <message> - Set offline message\n"
            settings_text += "/status - Show bot status\n"
            settings_text += "/help - Show help"
            
            await message.reply_text(settings_text)
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_set_offline_message(self, message: Message):
        """Set custom offline message"""
        try:
            # Extract message after command
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                await message.reply_text(
                    "ℹ️ **Usage:** /setoffline <your custom message>\n\n"
                    "Example: /setoffline I'm currently unavailable. I'll get back to you soon!"
                )
                return
            
            new_message = parts[1]
            if self.settings.set("offline_message", new_message):
                await message.reply_text(
                    f"✅ **Offline message updated!**\n\n"
                    f"New message:\n{new_message}"
                )
                logger.info(f"Offline message updated by owner")
            else:
                await message.reply_text("❌ Failed to update offline message.")
        except Exception as e:
            logger.error(f"Error setting offline message: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_help(self, message: Message):
        """Show help message"""
        try:
            help_text = (
                "📖 **CrushBot Help**\n\n"
                "**Available Commands:**\n\n"
                "/start - Start the bot\n"
                "/enable - Enable bot functionality\n"
                "/disable - Disable bot functionality\n"
                "/status - Show current bot status\n"
                "/settings - View all settings\n"
                "/setoffline <message> - Set custom offline message\n"
                "/help - Show this help message\n\n"
                "**Features:**\n"
                "• Automatically forwards messages to you\n"
                "• Sends offline notifications to senders\n"
                "• Alerts you of direct messages\n"
                "• Customizable settings and messages\n\n"
                "**Note:** Only you (the owner) can control this bot."
            )
            await message.reply_text(help_text)
        except Exception as e:
            logger.error(f"Error showing help: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_incoming_message(self, message: Message):
        """Handle incoming private messages from non-owner users"""
        try:
            # Check if bot is enabled
            if not self.settings.is_enabled():
                logger.info(f"Ignored message from {message.from_user.id} (bot disabled)")
                return
            
            sender = message.from_user
            sender_info = f"@{sender.username}" if sender.username else f"{sender.first_name}"
            sender_id = sender.id
            
            # Forward message to owner if enabled
            if self.settings.get("forward_messages"):
                try:
                    # Create forwarding header
                    forward_header = (
                        f"📨 **New Message**\n"
                        f"From: {sender_info} (ID: `{sender_id}`)\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"{'─' * 30}\n"
                    )
                    
                    # Send header to owner
                    await self.app.send_message(
                        Config.OWNER_ID,
                        forward_header
                    )
                    
                    # Forward the actual message
                    await message.forward(Config.OWNER_ID)
                    
                    logger.info(f"Forwarded message from {sender_id} to owner")
                except FloodWait as e:
                    logger.warning(f"FloodWait: sleeping for {e.value} seconds")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logger.error(f"Error forwarding message: {e}")
            
            # Send offline notification to sender if enabled
            if self.settings.get("offline_notification"):
                try:
                    offline_msg = self.settings.get_offline_message()
                    await message.reply_text(offline_msg)
                    logger.info(f"Sent offline notification to {sender_id}")
                except Exception as e:
                    logger.error(f"Error sending offline notification: {e}")
        
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
    
    async def handle_group_message(self, message: Message):
        """Handle messages in groups"""
        try:
            # Check if bot is enabled
            if not self.settings.is_enabled():
                return
            
            # Get bot info
            bot_me = await self.app.get_me()
            
            # Check if bot is mentioned or owner is mentioned
            mentioned_bot = False
            mentioned_owner = False
            
            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.MENTION:
                        mention = message.text[entity.offset:entity.offset + entity.length]
                        if mention == f"@{bot_me.username}":
                            mentioned_bot = True
                    elif entity.type == enums.MessageEntityType.TEXT_MENTION:
                        if entity.user.id == Config.OWNER_ID:
                            mentioned_owner = True
            
            # If bot is mentioned, send offline notification
            if mentioned_bot and message.from_user.id != Config.OWNER_ID:
                try:
                    offline_msg = self.settings.get_offline_message()
                    await message.reply_text(offline_msg)
                    
                    # Forward to owner
                    if self.settings.get("forward_messages"):
                        sender = message.from_user
                        sender_info = f"@{sender.username}" if sender.username else f"{sender.first_name}"
                        
                        notification = (
                            f"🏷️ **Bot Mentioned in Group**\n"
                            f"Group: {message.chat.title}\n"
                            f"From: {sender_info} (ID: `{sender.id}`)\n"
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"{'─' * 30}\n"
                        )
                        await self.app.send_message(Config.OWNER_ID, notification)
                        await message.forward(Config.OWNER_ID)
                    
                    logger.info(f"Bot mentioned in group {message.chat.id} by {message.from_user.id}")
                except Exception as e:
                    logger.error(f"Error handling bot mention: {e}")
            
            # If owner is mentioned or replied to, notify owner
            if (mentioned_owner or (message.reply_to_message and 
                message.reply_to_message.from_user.id == Config.OWNER_ID)) and \
                message.from_user.id != Config.OWNER_ID:
                
                if self.settings.get("direct_message_alerts"):
                    try:
                        sender = message.from_user
                        sender_info = f"@{sender.username}" if sender.username else f"{sender.first_name}"
                        
                        notification = (
                            f"💬 **Someone is trying to reach you!**\n"
                            f"Group: {message.chat.title}\n"
                            f"From: {sender_info} (ID: `{sender.id}`)\n"
                            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"{'─' * 30}\n"
                        )
                        await self.app.send_message(Config.OWNER_ID, notification)
                        await message.forward(Config.OWNER_ID)
                        
                        logger.info(f"Owner mentioned in group {message.chat.id} by {message.from_user.id}")
                    except Exception as e:
                        logger.error(f"Error notifying owner: {e}")
        
        except Exception as e:
            logger.error(f"Error handling group message: {e}")
    
    def run(self):
        """Start the bot"""
        try:
            logger.info("Starting CrushBot...")
            self.app.run()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Critical error: {e}")
            raise


def main():
    """Main entry point"""
    try:
        bot = CrushBot()
        bot.run()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("Required variables: API_ID, API_HASH, BOT_TOKEN, OWNER_ID")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
