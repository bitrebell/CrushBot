"""
User management command handlers for CrushBot
Includes ban, unban, and restrict commands
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from telegram import Update, ParseMode, ChatPermissions
from telegram.ext import CommandHandler, CallbackContext, Dispatcher
from telegram.error import BadRequest, TelegramError
from utils.helpers import (
    extract_user_and_text, 
    parse_duration, 
    get_readable_time, 
    is_admin
)
from utils.database import Database
from utils.logger import ActionLogger

logger = logging.getLogger(__name__)

def ban(update: Update, context: CallbackContext) -> None:
    """Ban a user from the group."""
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
    
    # Extract user ID and text from the command
    user_id, text = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text(
            "You must specify a user to ban. You can reply to a message or provide a username/user ID."
        )
        return
    
    # Check if user is trying to ban the bot
    if user_id == context.bot.id:
        message.reply_text("I'm not going to ban myself.")
        return
    
    # Check if user is trying to ban themselves
    if user_id == user.id:
        message.reply_text("You can't ban yourself.")
        return
    
    # Check if target user is an admin
    try:
        member = chat.get_member(user_id)
        if member.status in ['creator', 'administrator']:
            message.reply_text("I can't ban administrators.")
            return
    except BadRequest as e:
        message.reply_text(f"Error: {e.message}")
        return
    
    # Parse ban duration and reason
    duration_seconds = None
    reason = None
    
    if text:
        # Check for duration pattern at the beginning
        duration_match = re.match(r'(\d+[mhdw])\s*(.*)', text.strip())
        if duration_match:
            duration_str, remaining_text = duration_match.groups()
            duration_seconds = parse_duration(duration_str)
            reason = remaining_text.strip() if remaining_text else None
        else:
            # If no duration pattern found, assume the entire text is the reason
            reason = text.strip()
    
    # Get readable duration for logging
    duration_readable = get_readable_time(duration_seconds) if duration_seconds else "permanent"
    
    # Ban the user
    try:
        until_date = datetime.now() + timedelta(seconds=duration_seconds) if duration_seconds else None
        context.bot.kick_chat_member(
            chat_id=chat.id,
            user_id=user_id,
            until_date=until_date
        )
        
        # Prepare and send ban notification
        ban_message = f"User "
        
        try:
            # Try to get user mention
            banned_user = context.bot.get_chat_member(chat.id, user_id).user
            ban_message += f"[{banned_user.first_name}](tg://user?id={user_id})"
        except BadRequest:
            # Fallback to just showing user_id
            ban_message += f"`{user_id}`"
        
        ban_message += f" has been banned"
        
        if duration_seconds:
            ban_message += f" for {duration_readable}"
        
        if reason:
            ban_message += f"\nReason: {reason}"
        
        message.reply_text(
            ban_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log the ban if database and logger are available
        if 'db' in context.bot_data and 'logger' in context.bot_data:
            db = context.bot_data['db']
            action_logger = context.bot_data['logger']
            
            # Store ban in database
            ban_data = {
                'banned_by': user.id,
                'reason': reason,
                'expires_at': datetime.now() + timedelta(seconds=duration_seconds) if duration_seconds else None,
                'permanent': duration_seconds is None
            }
            db.ban_user(chat.id, user_id, ban_data)
            
            # Log the ban action
            action_logger.log_ban(
                group_id=chat.id,
                admin_id=user.id,
                user_id=user_id,
                reason=reason,
                duration=duration_seconds
            )
            
    except BadRequest as e:
        message.reply_text(f"Failed to ban user: {e.message}")
    except TelegramError as e:
        message.reply_text(f"An error occurred: {e.message}")

def unban(update: Update, context: CallbackContext) -> None:
    """Unban a user from the group."""
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
    
    # Extract user ID from the command
    user_id, _ = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text(
            "You must specify a user to unban. You can provide a username/user ID."
        )
        return
    
    # Check if user is trying to unban the bot
    if user_id == context.bot.id:
        message.reply_text("I'm not banned.")
        return
    
    # Try to unban the user
    try:
        context.bot.unban_chat_member(chat.id, user_id)
        
        # Send unban notification
        unban_message = f"User "
        
        try:
            # Try to get user mention
            unbanned_user = context.bot.get_chat(user_id)
            unban_message += f"[{unbanned_user.first_name}](tg://user?id={user_id})"
        except BadRequest:
            # Fallback to just showing user_id
            unban_message += f"`{user_id}`"
        
        unban_message += " has been unbanned"
        
        message.reply_text(
            unban_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log the unban if database and logger are available
        if 'db' in context.bot_data and 'logger' in context.bot_data:
            db = context.bot_data['db']
            action_logger = context.bot_data['logger']
            
            # Remove from ban list
            db.unban_user(chat.id, user_id)
            
            # Log the unban action
            action_logger.log_unban(
                group_id=chat.id,
                admin_id=user.id,
                user_id=user_id
            )
            
    except BadRequest as e:
        message.reply_text(f"Failed to unban user: {e.message}")
    except TelegramError as e:
        message.reply_text(f"An error occurred: {e.message}")

def restrict(update: Update, context: CallbackContext) -> None:
    """Restrict a user's permissions in the group."""
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
    
    # Extract user ID and text from the command
    user_id, text = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text(
            "You must specify a user to restrict. You can reply to a message or provide a username/user ID."
        )
        return
    
    # Check if user is trying to restrict the bot
    if user_id == context.bot.id:
        message.reply_text("I'm not going to restrict myself.")
        return
    
    # Check if user is trying to restrict themselves
    if user_id == user.id:
        message.reply_text("You can't restrict yourself.")
        return
    
    # Check if target user is an admin
    try:
        member = chat.get_member(user_id)
        if member.status in ['creator', 'administrator']:
            message.reply_text("I can't restrict administrators.")
            return
    except BadRequest as e:
        message.reply_text(f"Error: {e.message}")
        return
    
    # Default restrictions: everything disabled
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )
    
    # Parse custom restrictions and duration
    duration_seconds = None
    restriction_flags = {}
    
    if text:
        parts = text.strip().split()
        
        # Process each part
        for part in parts:
            # Check if it's a duration
            duration_match = re.match(r'(\d+[mhdw])', part)
            if duration_match:
                duration_str = duration_match.group(1)
                duration_seconds = parse_duration(duration_str)
                continue
            
            # Check if it's a permission flag
            if part.startswith('+') or part.startswith('-'):
                flag = part[1:]
                value = part.startswith('+')
                
                # Map flag to permission
                if flag == 'text':
                    restriction_flags['can_send_messages'] = value
                elif flag == 'media':
                    restriction_flags['can_send_media_messages'] = value
                elif flag == 'polls':
                    restriction_flags['can_send_polls'] = value
                elif flag == 'other':
                    restriction_flags['can_send_other_messages'] = value
                elif flag == 'web':
                    restriction_flags['can_add_web_page_previews'] = value
                elif flag == 'info':
                    restriction_flags['can_change_info'] = value
                elif flag == 'invite':
                    restriction_flags['can_invite_users'] = value
                elif flag == 'pin':
                    restriction_flags['can_pin_messages'] = value
                elif flag == 'all':
                    # Set all permissions to the same value
                    restriction_flags = {
                        'can_send_messages': value,
                        'can_send_media_messages': value,
                        'can_send_polls': value,
                        'can_send_other_messages': value,
                        'can_add_web_page_previews': value,
                        'can_change_info': value,
                        'can_invite_users': value,
                        'can_pin_messages': value
                    }
    
    # Apply custom restrictions if any were specified
    if restriction_flags:
        permissions_dict = {
            'can_send_messages': False,
            'can_send_media_messages': False,
            'can_send_polls': False,
            'can_send_other_messages': False,
            'can_add_web_page_previews': False,
            'can_change_info': False,
            'can_invite_users': False,
            'can_pin_messages': False
        }
        
        # Update with any flags that were specified
        permissions_dict.update(restriction_flags)
        
        # Create new permissions object
        permissions = ChatPermissions(**permissions_dict)
    
    # Get readable duration for logging
    duration_readable = get_readable_time(duration_seconds) if duration_seconds else "permanent"
    
    # Apply the restrictions
    try:
        until_date = datetime.now() + timedelta(seconds=duration_seconds) if duration_seconds else None
        context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=user_id,
            permissions=permissions,
            until_date=until_date
        )
        
        # Prepare and send restrict notification
        restrict_message = f"User "
        
        try:
            # Try to get user mention
            restricted_user = context.bot.get_chat_member(chat.id, user_id).user
            restrict_message += f"[{restricted_user.first_name}](tg://user?id={user_id})"
        except BadRequest:
            # Fallback to just showing user_id
            restrict_message += f"`{user_id}`"
        
        restrict_message += f" has been restricted"
        
        if duration_seconds:
            restrict_message += f" for {duration_readable}"
        
        message.reply_text(
            restrict_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log the restriction if logger is available
        if 'logger' in context.bot_data:
            action_logger = context.bot_data['logger']
            
            # Log the restrict action
            action_logger.log_restrict(
                group_id=chat.id,
                admin_id=user.id,
                user_id=user_id,
                restrictions=restriction_flags,
                duration=duration_seconds
            )
            
    except BadRequest as e:
        message.reply_text(f"Failed to restrict user: {e.message}")
    except TelegramError as e:
        message.reply_text(f"An error occurred: {e.message}")

def banlist(update: Update, context: CallbackContext) -> None:
    """Show a list of banned users in the group."""
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
    
    db = context.bot_data['db']
    
    # Get banned users from database
    banned_users = db.get_banned_users(chat.id)
    
    if not banned_users:
        message.reply_text("There are no banned users in this group.")
        return
    
    # Prepare banlist message
    banlist_text = "🚫 *Banned Users*\n\n"
    
    for banned in banned_users:
        user_id = banned['user_id']
        reason = banned.get('reason', 'No reason provided')
        permanent = banned.get('permanent', True)
        expires_at = banned.get('expires_at')
        
        # Try to get user's name
        try:
            user = context.bot.get_chat(user_id)
            user_name = user.first_name
        except (BadRequest, TelegramError):
            user_name = f"User {user_id}"
        
        banlist_text += f"• [{user_name}](tg://user?id={user_id})"
        
        if not permanent and expires_at:
            # Calculate time remaining
            now = datetime.now()
            if expires_at > now:
                time_remaining = expires_at - now
                readable_time = get_readable_time(int(time_remaining.total_seconds()))
                banlist_text += f" - Banned for {readable_time} more"
            else:
                banlist_text += " - Ban expired"
        else:
            banlist_text += " - Permanently banned"
            
        banlist_text += f"\n  Reason: {reason}\n\n"
    
    # Send the banlist (paginate if needed)
    if len(banlist_text) > 4000:
        # Split into multiple messages
        parts = [banlist_text[i:i+4000] for i in range(0, len(banlist_text), 4000)]
        for i, part in enumerate(parts):
            if i == 0:
                message.reply_text(
                    part,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                context.bot.send_message(
                    chat_id=chat.id,
                    text=part,
                    parse_mode=ParseMode.MARKDOWN
                )
    else:
        message.reply_text(
            banlist_text,
            parse_mode=ParseMode.MARKDOWN
        )

def register_user_management_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database, 
    action_logger: ActionLogger
) -> None:
    """Register all user management command handlers."""
    # Store database and logger in bot_data for access in handlers
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['logger'] = action_logger
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("ban", ban))
    dispatcher.add_handler(CommandHandler("unban", unban))
    dispatcher.add_handler(CommandHandler("restrict", restrict))
    dispatcher.add_handler(CommandHandler("banlist", banlist))
    
    logger.info("User management command handlers registered") 