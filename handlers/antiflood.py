"""
Anti-flood protection for CrushBot
Prevents spam by limiting message frequency
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from telegram import Update, ChatPermissions, ParseMode
from telegram.ext import MessageHandler, Filters, CallbackContext, Dispatcher
from telegram.error import BadRequest, TelegramError

from utils.helpers import is_admin
from utils.database import Database

logger = logging.getLogger(__name__)

# Store user message counts for antiflood
flood_data = defaultdict(lambda: defaultdict(lambda: {"count": 0, "last_update": time.time()}))

def check_flood(update: Update, context: CallbackContext) -> None:
    """Check and handle message flooding."""
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
    
    # Check if antiflood feature is enabled
    if not config.get('features', {}).get('antiflood', False):
        return
    
    # Get antiflood settings
    antiflood = config.get('antiflood', {})
    limit = antiflood.get('limit', 10)
    time_window = antiflood.get('time', 15)
    action = antiflood.get('action', 'mute')
    duration = antiflood.get('duration', 900)  # Default 15 minutes
    
    # Get group-specific settings from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id)
        
        if group_data and 'antiflood' in group_data:
            group_antiflood = group_data['antiflood']
            limit = group_antiflood.get('limit', limit)
            time_window = group_antiflood.get('time', time_window)
            action = group_antiflood.get('action', action)
            duration = group_antiflood.get('duration', duration)
    
    # Check if user is flooding
    current_time = time.time()
    user_data = flood_data[chat.id][user.id]
    user_data['count'] += 1
    
    # Reset counter if enough time has passed
    if current_time - user_data['last_update'] > time_window:
        user_data['count'] = 1
    
    user_data['last_update'] = current_time
    
    # If user is flooding, take action
    if user_data['count'] > limit:
        # Reset flood counter after taking action
        user_data['count'] = 0
        
        if action == 'ban':
            take_flood_action(update, context, 'ban', duration)
        elif action == 'kick':
            take_flood_action(update, context, 'kick')
        elif action == 'mute':
            take_flood_action(update, context, 'mute', duration)
        else:
            # Default to warn
            message.reply_text(f"Please don't flood the chat! You're sending messages too quickly.")

def take_flood_action(update: Update, context: CallbackContext, action: str, duration: Optional[int] = None) -> None:
    """Take action against a flooding user."""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    
    readable_action = action.capitalize()
    duration_text = f" for {duration // 60} minutes" if duration else ""
    action_message = f"{readable_action}ning {user.first_name} due to flooding{duration_text}."
    
    try:
        if action == 'ban':
            # Permanent ban if duration is None
            until_date = datetime.now() + timedelta(seconds=duration) if duration else None
            context.bot.kick_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                until_date=until_date
            )
        elif action == 'kick':
            # Kick and unban immediately
            context.bot.kick_chat_member(chat_id=chat.id, user_id=user.id)
            context.bot.unban_chat_member(chat_id=chat.id, user_id=user.id)
        elif action == 'mute':
            # Restrict ability to send messages
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            until_date = datetime.now() + timedelta(seconds=duration) if duration else None
            context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=permissions,
                until_date=until_date
            )
        
        # Send notification
        message.reply_text(
            action_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log the action if logger is available
        if 'logger' in context.bot_data:
            action_logger = context.bot_data['logger']
            
            if action == 'ban':
                action_logger.log_ban(
                    group_id=chat.id,
                    admin_id=context.bot.id,
                    user_id=user.id,
                    reason="Flooding",
                    duration=duration
                )
            elif action == 'mute':
                restrictions = {'can_send_messages': False}
                action_logger.log_restrict(
                    group_id=chat.id,
                    admin_id=context.bot.id,
                    user_id=user.id,
                    restrictions=restrictions,
                    duration=duration
                )
    
    except BadRequest as e:
        message.reply_text(f"Failed to {action} user: {e.message}")
    except TelegramError as e:
        message.reply_text(f"An error occurred: {e.message}")

def set_antiflood(update: Update, context: CallbackContext) -> None:
    """Set antiflood settings for a group."""
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
    if not context.args or len(context.args) < 1:
        message.reply_text(
            "Please provide settings. Usage:\n"
            "/setflood <limit|off> [time] [action] [duration]\n\n"
            "Examples:\n"
            "/setflood 10 - Set limit to 10 messages\n"
            "/setflood 5 10 - 5 messages in 10 seconds\n"
            "/setflood 5 10 mute 300 - 5 messages in 10 seconds = mute for 5 minutes\n"
            "/setflood off - Disable antiflood"
        )
        return
    
    # Parse arguments
    limit = context.args[0].lower()
    
    # Check if antiflood should be disabled
    if limit == 'off' or limit == '0':
        # Update database
        if 'db' in context.bot_data:
            db = context.bot_data['db']
            db.update_group_setting(chat.id, 'antiflood.enabled', False)
            
            message.reply_text("Antiflood protection has been disabled.")
            
            # Log action if logger is available
            if 'logger' in context.bot_data:
                action_logger = context.bot_data['logger']
                action_logger.log_action(
                    group_id=chat.id,
                    admin_id=user.id,
                    action_type='settings_change',
                    details={'setting': 'antiflood', 'value': 'disabled'}
                )
        return
    
    # Parse limit
    try:
        limit = int(limit)
        if limit < 3:
            message.reply_text("Antiflood limit must be at least 3.")
            return
    except ValueError:
        message.reply_text("Antiflood limit must be a number or 'off'.")
        return
    
    # Parse time window
    time_window = 15  # Default: 15 seconds
    if len(context.args) >= 2:
        try:
            time_window = int(context.args[1])
            if time_window < 3:
                message.reply_text("Time window must be at least 3 seconds.")
                return
        except ValueError:
            message.reply_text("Time window must be a number.")
            return
    
    # Parse action
    action = 'mute'  # Default: mute
    if len(context.args) >= 3:
        action = context.args[2].lower()
        if action not in ['ban', 'kick', 'mute']:
            message.reply_text("Action must be one of: ban, kick, mute.")
            return
    
    # Parse duration
    duration = 900  # Default: 15 minutes
    if len(context.args) >= 4:
        try:
            duration = int(context.args[3])
            if duration < 30:
                message.reply_text("Duration must be at least 30 seconds.")
                return
        except ValueError:
            message.reply_text("Duration must be a number.")
            return
    
    # Update database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        antiflood_settings = {
            'enabled': True,
            'limit': limit,
            'time': time_window,
            'action': action,
            'duration': duration
        }
        db.update_group_setting(chat.id, 'antiflood', antiflood_settings)
        
        action_text = f"{action} for {duration // 60} minutes" if action in ['ban', 'mute'] else action
        message.reply_text(
            f"Antiflood settings updated.\n"
            f"Limit: {limit} messages\n"
            f"Time window: {time_window} seconds\n"
            f"Action: {action_text}"
        )
        
        # Log action if logger is available
        if 'logger' in context.bot_data:
            action_logger = context.bot_data['logger']
            action_logger.log_action(
                group_id=chat.id,
                admin_id=user.id,
                action_type='settings_change',
                details={'setting': 'antiflood', 'value': antiflood_settings}
            )

def register_antiflood_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database
) -> None:
    """Register antiflood handlers."""
    # Store database reference
    dispatcher.bot_data['db'] = db
    
    # Register command handlers
    dispatcher.add_handler(MessageHandler(
        Filters.all & ~Filters.status_update & ~Filters.command & ~Filters.chat_type.private,
        check_flood
    ))
    dispatcher.add_handler(MessageHandler(Filters.command & Filters.regex(r'^/setflood'), set_antiflood))
    
    logger.info("Antiflood handlers registered") 