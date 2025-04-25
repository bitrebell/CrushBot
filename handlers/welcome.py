"""
Welcome message handlers for CrushBot
Handles welcome messages for new members joining a group
"""

import logging
from typing import Dict, Any, Optional, List
from telegram import Update, ParseMode, User, Chat
from telegram.ext import MessageHandler, Filters, CallbackContext, CommandHandler, Dispatcher
from utils.helpers import is_admin
from utils.database import Database

logger = logging.getLogger(__name__)

def format_welcome_message(message_template: str, user: User, chat: Chat) -> str:
    """
    Format the welcome message with user and group details.
    
    Args:
        message_template: The welcome message template
        user: The user who joined
        chat: The chat they joined
        
    Returns:
        Formatted welcome message
    """
    # Basic formatting
    message = message_template.replace('{user}', f"[{user.first_name}](tg://user?id={user.id})")
    message = message.replace('{group}', chat.title)
    
    # Additional optional formatting
    message = message.replace('{username}', f"@{user.username}" if user.username else user.first_name)
    message = message.replace('{userid}', str(user.id))
    message = message.replace('{first}', user.first_name)
    message = message.replace('{last}', user.last_name if user.last_name else '')
    message = message.replace('{chatid}', str(chat.id))
    
    return message

def welcome_new_members(update: Update, context: CallbackContext) -> None:
    """Send welcome message when new members join the group."""
    chat = update.effective_chat
    message = update.effective_message
    
    # Make sure this is a group
    if chat.type not in ['group', 'supergroup']:
        return
    
    # Check if welcome messages are enabled in config
    if 'config' in context.bot_data:
        config = context.bot_data['config']
        if 'features' in config and not config['features'].get('welcome_message', True):
            return
    
    # Get new members
    new_members = message.new_chat_members
    
    # Skip if no new members or if the new member is the bot itself
    if not new_members:
        return
    
    # Get database
    if 'db' not in context.bot_data:
        logger.error("Database not available for welcome message")
        return
    
    db = context.bot_data['db']
    
    # Get group data
    group_data = db.get_group(chat.id)
    welcome_message_template = None
    
    # Check if group has a custom welcome message
    if group_data and 'welcome_message' in group_data:
        welcome_message_template = group_data['welcome_message']
    
    # If no custom message, use default from config
    if not welcome_message_template and 'config' in context.bot_data:
        config = context.bot_data['config']
        if 'messages' in config and 'welcome' in config['messages']:
            welcome_message_template = config['messages']['welcome']
    
    # If still no message, use hardcoded default
    if not welcome_message_template:
        welcome_message_template = "Welcome {user} to {group}!"
    
    # Process each new member
    for new_member in new_members:
        # Skip if the new member is the bot itself
        if new_member.id == context.bot.id:
            continue
        
        # Format welcome message for this user
        formatted_message = format_welcome_message(welcome_message_template, new_member, chat)
        
        # Add rules if they exist
        if group_data and 'rules' in group_data and group_data['rules']:
            formatted_message += f"\n\n*Group Rules:*\n{group_data['rules']}"
        
        # Send welcome message
        try:
            context.bot.send_message(
                chat_id=chat.id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

def set_welcome_message(update: Update, context: CallbackContext) -> None:
    """Set custom welcome message for a group."""
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
    
    # Check if there's a message to set
    if not context.args:
        message.reply_text(
            "Please provide a welcome message. You can use these placeholders:\n"
            "{user} - User mention with link\n"
            "{username} - Username or first name\n"
            "{first} - First name\n"
            "{last} - Last name\n"
            "{group} - Group name\n"
            "\nExample: /setwelcome Welcome {user} to {group}!"
        )
        return
    
    # Get welcome message text
    welcome_text = ' '.join(context.args)
    
    # Save to database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        db.update_group_setting(chat.id, 'welcome_message', welcome_text)
        
        message.reply_text("Welcome message has been updated successfully.")
        
        # Log action if logger is available
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_welcome_set(
                group_id=chat.id,
                admin_id=user.id,
                welcome_message=welcome_text
            )

def reset_welcome_message(update: Update, context: CallbackContext) -> None:
    """Reset welcome message to default."""
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
    
    # Reset welcome message in database (remove setting)
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        
        # Get group data
        group_data = db.get_group(chat.id)
        
        if group_data and 'welcome_message' in group_data:
            # Update group to remove welcome_message
            db.update_group_setting(chat.id, 'welcome_message', None)
            
            message.reply_text("Welcome message has been reset to default.")
            
            # Log action if logger is available
            if 'logger' in context.bot_data:
                logger = context.bot_data['logger']
                logger.log_action(
                    group_id=chat.id,
                    admin_id=user.id,
                    action_type='welcome_reset'
                )
        else:
            message.reply_text("No custom welcome message was set for this group.")

def register_welcome_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database
) -> None:
    """Register welcome message handlers."""
    # Register message handlers
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new_members))
    dispatcher.add_handler(CommandHandler("setwelcome", set_welcome_message))
    dispatcher.add_handler(CommandHandler("resetwelcome", reset_welcome_message))
    
    logger.info("Welcome message handlers registered") 