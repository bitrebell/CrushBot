"""
Blacklist filter for CrushBot
Filters and removes messages containing blacklisted words
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set

from telegram import Update, ParseMode
from telegram.ext import MessageHandler, Filters, CallbackContext, CommandHandler, Dispatcher
from telegram.error import BadRequest, TelegramError

from utils.helpers import is_admin
from utils.database import Database

logger = logging.getLogger(__name__)

def filter_blacklist(update: Update, context: CallbackContext) -> None:
    """Filter messages containing blacklisted words."""
    # Skip if not in group or supergroup
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    if not chat or chat.type not in ['group', 'supergroup']:
        return
    
    # Skip if user is admin
    if is_admin(update, context):
        return
    
    # Get config from bot_data
    if 'config' not in context.bot_data:
        return
    
    config = context.bot_data['config']
    
    # Check if blacklist feature is enabled
    if not config.get('features', {}).get('blacklist_words', False):
        return
    
    # Get blacklist from config and database
    blacklisted_words = set(config.get('blacklist', []))
    
    # Get group-specific blacklist from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id)
        
        if group_data and 'blacklist' in group_data:
            blacklisted_words.update(group_data.get('blacklist', []))
    
    if not blacklisted_words:
        return
    
    # Check message text
    if message.text:
        message_text = message.text.lower()
        
        # Check if any blacklisted words are in the message
        triggered_words = []
        for word in blacklisted_words:
            pattern = r'\b' + re.escape(word.lower()) + r'\b'
            if re.search(pattern, message_text):
                triggered_words.append(word)
        
        if triggered_words:
            try:
                # Delete the message
                message.delete()
                
                # Notify in the chat (optional)
                warning = f"Message from {user.first_name} deleted due to blacklisted word."
                context.bot.send_message(
                    chat_id=chat.id,
                    text=warning,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Log the action if logger is available
                if 'logger' in context.bot_data:
                    action_logger = context.bot_data['logger']
                    action_logger.log_action(
                        group_id=chat.id,
                        admin_id=context.bot.id,
                        action_type='blacklist_triggered',
                        target_user_id=user.id,
                        details={'words': triggered_words}
                    )
                
            except BadRequest as e:
                logger.error(f"Error deleting blacklisted message: {e}")
            except TelegramError as e:
                logger.error(f"Telegram error: {e}")

def blacklist_add(update: Update, context: CallbackContext) -> None:
    """Add words to the blacklist."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        message.reply_text("This command can only be used in groups.")
        return
    
    # Check if user is an admin
    if not is_admin(update, context):
        message.reply_text("This command can only be used by group admins.")
        return
    
    # Check if there are arguments
    if not context.args:
        message.reply_text(
            "Please provide words to blacklist.\n"
            "Example: /blacklist add word1 word2 word3"
        )
        return
    
    # Get words to add
    words_to_add = [word.lower() for word in context.args]
    
    # Update database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id) or {}
        
        # Get existing blacklist
        current_blacklist = set(group_data.get('blacklist', []))
        
        # Add new words
        current_blacklist.update(words_to_add)
        
        # Update database
        db.update_group_setting(chat.id, 'blacklist', list(current_blacklist))
        
        # Notify
        added_words = ", ".join([f"`{word}`" for word in words_to_add])
        message.reply_text(
            f"Added {len(words_to_add)} words to the blacklist:\n{added_words}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log action if logger is available
        if 'logger' in context.bot_data:
            action_logger = context.bot_data['logger']
            action_logger.log_action(
                group_id=chat.id,
                admin_id=user.id,
                action_type='blacklist_update',
                details={'added': words_to_add}
            )

def blacklist_remove(update: Update, context: CallbackContext) -> None:
    """Remove words from the blacklist."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        message.reply_text("This command can only be used in groups.")
        return
    
    # Check if user is an admin
    if not is_admin(update, context):
        message.reply_text("This command can only be used by group admins.")
        return
    
    # Check if there are arguments
    if not context.args:
        message.reply_text(
            "Please provide words to remove from blacklist.\n"
            "Example: /blacklist remove word1 word2 word3"
        )
        return
    
    # Get words to remove
    words_to_remove = [word.lower() for word in context.args]
    
    # Update database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id) or {}
        
        # Get existing blacklist
        current_blacklist = set(group_data.get('blacklist', []))
        
        # Check if words exist in blacklist
        existing_words = [word for word in words_to_remove if word in current_blacklist]
        
        if not existing_words:
            message.reply_text("None of these words were found in the blacklist.")
            return
        
        # Remove words
        for word in existing_words:
            current_blacklist.remove(word)
        
        # Update database
        db.update_group_setting(chat.id, 'blacklist', list(current_blacklist))
        
        # Notify
        removed_words = ", ".join([f"`{word}`" for word in existing_words])
        message.reply_text(
            f"Removed {len(existing_words)} words from the blacklist:\n{removed_words}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log action if logger is available
        if 'logger' in context.bot_data:
            action_logger = context.bot_data['logger']
            action_logger.log_action(
                group_id=chat.id,
                admin_id=user.id,
                action_type='blacklist_update',
                details={'removed': existing_words}
            )

def blacklist_list(update: Update, context: CallbackContext) -> None:
    """List all blacklisted words."""
    chat = update.effective_chat
    message = update.effective_message
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        message.reply_text("This command can only be used in groups.")
        return
    
    # Check if user is an admin
    if not is_admin(update, context):
        message.reply_text("This command can only be used by group admins.")
        return
    
    # Get blacklist from config and database
    config = context.bot_data.get('config', {})
    blacklisted_words = set(config.get('blacklist', []))
    
    # Get group-specific blacklist from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id)
        
        if group_data and 'blacklist' in group_data:
            blacklisted_words.update(group_data.get('blacklist', []))
    
    if not blacklisted_words:
        message.reply_text("There are no blacklisted words in this chat.")
        return
    
    # Format blacklist
    blacklist_text = "\n".join([f"• `{word}`" for word in sorted(blacklisted_words)])
    
    message.reply_text(
        f"🚫 *Blacklisted Words in this Chat:*\n\n{blacklist_text}",
        parse_mode=ParseMode.MARKDOWN
    )

def blacklist_command(update: Update, context: CallbackContext) -> None:
    """Handle all blacklist commands."""
    message = update.effective_message
    
    if not context.args:
        # Show help
        message.reply_text(
            "Usage:\n"
            "/blacklist add <words> - Add words to the blacklist\n"
            "/blacklist remove <words> - Remove words from the blacklist\n"
            "/blacklist list - Show all blacklisted words"
        )
        return
    
    # Parse subcommand
    subcommand = context.args[0].lower()
    context.args = context.args[1:]
    
    if subcommand == 'add':
        blacklist_add(update, context)
    elif subcommand == 'remove':
        blacklist_remove(update, context)
    elif subcommand == 'list':
        blacklist_list(update, context)
    else:
        message.reply_text(
            f"Unknown subcommand: {subcommand}\n"
            "Use: add, remove, or list"
        )

def register_blacklist_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database
) -> None:
    """Register blacklist handlers."""
    # Store config and database reference
    dispatcher.bot_data['config'] = config
    dispatcher.bot_data['db'] = db
    
    # Register message handler for filtering
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command & ~Filters.chat_type.private,
        filter_blacklist,
        run_async=True
    ))
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler(
        "blacklist", 
        blacklist_command,
        run_async=True
    ))
    
    logger.info("Blacklist handlers registered") 