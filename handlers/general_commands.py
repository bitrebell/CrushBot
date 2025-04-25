"""
General command handlers for CrushBot
Includes start, help, rules, and other basic commands
"""

import logging
from typing import Dict, Any
from telegram import Update, ParseMode
from telegram.ext import CommandHandler, CallbackContext, Dispatcher
from utils.helpers import is_admin

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Handle the /start command - introduce the bot."""
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    if chat_type == 'private':
        # Private chat with the bot
        message = (
            f"Hello {user.first_name}! I'm CrushBot, a Telegram group management bot.\n\n"
            f"Add me to your group and I'll help you manage it with advanced features.\n\n"
            f"Use /help to see available commands."
        )
    else:
        # Group chat
        message = (
            f"I'm CrushBot, a Telegram group management bot.\n"
            f"Use /help to see available commands."
        )
    
    update.message.reply_text(message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Display help message with available commands."""
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    # Check if user is an admin
    is_user_admin = is_admin(update, context)
    
    help_text = "📝 *Available Commands*\n\n"
    
    # General commands for all users
    help_text += "*General Commands:*\n"
    help_text += "• /start - Start the bot\n"
    help_text += "• /help - Show this help message\n"
    help_text += "• /rules - Show group rules\n\n"
    
    # Admin commands - only show if user is an admin
    if is_user_admin:
        help_text += "*Admin Commands:*\n"
        help_text += "• /ban <user> [duration] [reason] - Ban a user\n"
        help_text += "• /unban <user> - Unban a user\n"
        help_text += "• /restrict <user> [permissions] [duration] - Restrict user permissions\n"
        help_text += "• /banlist - Show list of banned users\n"
        help_text += "• /logs [number] - Show recent action logs\n"
        help_text += "• /setwelcome <message> - Set custom welcome message\n"
        help_text += "• /resetwelcome - Reset welcome message to default\n"
    
    update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

def rules(update: Update, context: CallbackContext) -> None:
    """Display group rules if set."""
    chat = update.effective_chat
    
    if chat.type not in ['group', 'supergroup']:
        update.message.reply_text("This command can only be used in groups.")
        return
    
    # Check if rules are set in the database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id)
        
        if group_data and 'rules' in group_data and group_data['rules']:
            rules_text = f"📋 *Group Rules*\n\n{group_data['rules']}"
            update.message.reply_text(
                rules_text,
                parse_mode=ParseMode.MARKDOWN
            )
            return
    
    # Default message if no rules are set
    update.message.reply_text(
        "No rules have been set for this group yet. Admins can set rules with /setrules command."
    )

def set_rules(update: Update, context: CallbackContext) -> None:
    """Set group rules."""
    chat = update.effective_chat
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        update.message.reply_text("This command can only be used in groups.")
        return
    
    # Check if user is an admin
    if not is_admin(update, context):
        update.message.reply_text("This command can only be used by group admins.")
        return
    
    # Get rules text
    if not context.args:
        update.message.reply_text(
            "Please provide rules text. Example: /setrules No spamming. Be respectful."
        )
        return
    
    rules_text = ' '.join(context.args)
    
    # Save rules to database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        db.update_group_setting(chat.id, 'rules', rules_text)
        
        update.message.reply_text("Group rules have been updated successfully.")
        
        # Log action if logger is available
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_action(
                group_id=chat.id,
                admin_id=update.effective_user.id,
                action_type='rules_set',
                details={'rules': rules_text}
            )

def register_general_handlers(dispatcher: Dispatcher, config: Dict[str, Any]) -> None:
    """Register all general command handlers."""
    # Store config in bot_data for access in handlers
    dispatcher.bot_data['config'] = config
    
    # If admins list exists in config, store it in bot_data
    if 'admins' in config:
        dispatcher.bot_data['admins'] = config['admins']
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("rules", rules))
    dispatcher.add_handler(CommandHandler("setrules", set_rules))
    
    logger.info("General command handlers registered") 