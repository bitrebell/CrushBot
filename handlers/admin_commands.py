"""
Admin command handlers for CrushBot
Includes logs viewing and other admin-specific commands
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from telegram import Update, ParseMode
from telegram.ext import CommandHandler, CallbackContext, Dispatcher
from telegram.error import BadRequest, TelegramError
from utils.helpers import is_admin, get_readable_time
from utils.database import Database
from utils.logger import ActionLogger

logger = logging.getLogger(__name__)

def format_log_entry(log_entry: Dict[str, Any], context: CallbackContext) -> str:
    """
    Format a log entry for display.
    
    Args:
        log_entry: The log entry to format
        context: The callback context
        
    Returns:
        Formatted log entry as string
    """
    # Extract basic info
    timestamp = log_entry.get('timestamp', datetime.now())
    action_type = log_entry.get('action_type', 'unknown')
    admin_id = log_entry.get('admin_id')
    target_user_id = log_entry.get('target_user_id')
    details = log_entry.get('details', {})
    
    # Format timestamp
    timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format admin name
    admin_name = f"Admin {admin_id}"
    try:
        admin = context.bot.get_chat(admin_id)
        admin_name = admin.first_name
        if admin.username:
            admin_name = f"@{admin.username}"
    except (BadRequest, TelegramError):
        pass
    
    # Format target user name if applicable
    target_user_str = ""
    if target_user_id:
        target_user_name = f"User {target_user_id}"
        try:
            target_user = context.bot.get_chat(target_user_id)
            target_user_name = target_user.first_name
            if target_user.username:
                target_user_name = f"@{target_user.username}"
            target_user_str = f" on [{target_user_name}](tg://user?id={target_user_id})"
        except (BadRequest, TelegramError):
            target_user_str = f" on User {target_user_id}"
    
    # Format action type
    action_str = action_type.replace('_', ' ').title()
    
    # Format details based on action type
    details_str = ""
    if action_type == 'ban':
        reason = details.get('reason', 'No reason provided')
        duration = details.get('duration')
        if duration:
            duration_str = get_readable_time(duration)
            details_str = f"for {duration_str}\nReason: {reason}"
        else:
            details_str = f"permanently\nReason: {reason}"
    elif action_type == 'restrict':
        restrictions = details.get('restrictions', {})
        duration = details.get('duration')
        
        restrictions_str = ", ".join([
            k.replace('can_', '').replace('_', ' ')
            for k, v in restrictions.items() if v
        ])
        
        if not restrictions_str:
            restrictions_str = "all actions"
        
        if duration:
            duration_str = get_readable_time(duration)
            details_str = f"from {restrictions_str} for {duration_str}"
        else:
            details_str = f"from {restrictions_str} permanently"
    elif action_type == 'welcome_set':
        message = details.get('message', '')
        if len(message) > 50:
            message = message[:47] + '...'
        details_str = f"to: {message}"
    
    # Combine all parts
    log_str = f"*{timestamp_str}*: {admin_name} performed *{action_str}*{target_user_str}"
    if details_str:
        log_str += f"\n{details_str}"
    
    return log_str

def logs(update: Update, context: CallbackContext) -> None:
    """Show recent action logs in the group."""
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
    
    # Check if database is available
    if 'db' not in context.bot_data:
        message.reply_text("Database is not available.")
        return
    
    # Parse limit argument
    limit = 10  # Default
    if context.args and context.args[0].isdigit():
        limit = int(context.args[0])
        limit = max(1, min(limit, 50))  # Keep between 1 and 50
    
    db = context.bot_data['db']
    
    # Get logs from database
    logs = db.get_logs(chat.id, limit)
    
    if not logs:
        message.reply_text("No action logs found for this group.")
        return
    
    # Prepare logs message
    logs_text = f"📝 *Recent Actions in {chat.title}*\n\n"
    
    for log_entry in logs:
        logs_text += format_log_entry(log_entry, context) + "\n\n"
    
    # Send the logs
    try:
        message.reply_text(
            logs_text,
            parse_mode=ParseMode.MARKDOWN
        )
    except BadRequest:
        # If parsing fails, try without markdown
        message.reply_text(
            "Error formatting logs with markdown. Here are the raw logs:\n\n" +
            logs_text.replace('*', '')
        )

def register_admin_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database, 
    action_logger: ActionLogger
) -> None:
    """Register admin command handlers."""
    # Register command handlers
    dispatcher.add_handler(CommandHandler("logs", logs))
    
    logger.info("Admin command handlers registered") 