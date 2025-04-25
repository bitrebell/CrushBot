"""
Warning system for CrushBot
Allows admins to warn users and takes automatic actions after a threshold
"""

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union

from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Dispatcher
from telegram.error import BadRequest, TelegramError

from utils.helpers import extract_user_and_text, is_admin, get_readable_time
from utils.database import Database
from utils.logger import ActionLogger

logger = logging.getLogger(__name__)

def warn_user(update: Update, context: CallbackContext) -> None:
    """Warn a user."""
    chat = update.effective_chat
    admin = update.effective_user
    message = update.effective_message
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        message.reply_text("This command can only be used in groups.")
        return
    
    # Check if user is an admin
    if not is_admin(update, context):
        message.reply_text("This command can only be used by group admins.")
        return
    
    # Extract user ID and reason from the command
    user_id, reason = extract_user_and_text(update, context)
    
    if not user_id:
        message.reply_text(
            "You must specify a user to warn. You can reply to a message or provide a username/user ID."
        )
        return
    
    # Check if user is trying to warn the bot
    if user_id == context.bot.id:
        message.reply_text("I'm not going to warn myself.")
        return
    
    # Check if user is trying to warn themselves
    if user_id == admin.id:
        message.reply_text("You can't warn yourself.")
        return
    
    # Check if target user is an admin
    try:
        member = chat.get_member(user_id)
        if member.status in ['creator', 'administrator']:
            message.reply_text("I can't warn administrators.")
            return
        target_user = member.user
    except BadRequest as e:
        message.reply_text(f"Error: {e.message}")
        return
    
    # Get config
    config = context.bot_data.get('config', {})
    
    # Get warn settings
    warn_settings = config.get('restrictions', {})
    warn_limit = warn_settings.get('warn_limit', 3)
    warn_expiry = warn_settings.get('warn_expiry', 604800)  # 7 days in seconds
    warn_punishment = warn_settings.get('warn_punishment', 'ban')
    
    # Check if group has custom warn settings
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        group_data = db.get_group(chat.id)
        
        if group_data and 'warns' in group_data:
            group_warns = group_data['warns']
            warn_limit = group_warns.get('limit', warn_limit)
            warn_expiry = group_warns.get('expiry', warn_expiry)
            warn_punishment = group_warns.get('punishment', warn_punishment)
    
    # Add warn to database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        
        # Get existing warns for user
        warns_data = db.get_user_warns(chat.id, user_id) or []
        
        # Remove expired warns
        current_time = time.time()
        active_warns = [
            w for w in warns_data 
            if not w.get('expiry') or w.get('expiry', 0) > current_time
        ]
        
        # Add new warn
        warn_data = {
            'reason': reason or "No reason provided",
            'admin_id': admin.id,
            'timestamp': current_time,
            'expiry': current_time + warn_expiry if warn_expiry else None
        }
        active_warns.append(warn_data)
        
        # Save to database
        db.update_user_warns(chat.id, user_id, active_warns)
        
        # Check if user has reached the warn limit
        if len(active_warns) >= warn_limit:
            # Reset warns after taking action
            db.clear_user_warns(chat.id, user_id)
            
            # Take punishment action
            if warn_punishment == 'ban':
                try:
                    context.bot.kick_chat_member(chat.id, user_id)
                    message.reply_text(
                        f"User {target_user.first_name} has been banned after receiving {warn_limit} warnings."
                    )
                    # Log action
                    if 'logger' in context.bot_data:
                        logger = context.bot_data['logger']
                        logger.log_ban(
                            group_id=chat.id,
                            admin_id=context.bot.id,
                            user_id=user_id,
                            reason=f"Reached warn limit ({warn_limit})"
                        )
                except BadRequest as e:
                    message.reply_text(f"Failed to ban user: {e.message}")
            
            elif warn_punishment == 'kick':
                try:
                    context.bot.kick_chat_member(chat.id, user_id)
                    context.bot.unban_chat_member(chat.id, user_id)
                    message.reply_text(
                        f"User {target_user.first_name} has been kicked after receiving {warn_limit} warnings."
                    )
                    # Log action
                    if 'logger' in context.bot_data:
                        logger = context.bot_data['logger']
                        logger.log_action(
                            group_id=chat.id,
                            admin_id=context.bot.id,
                            action_type='kick',
                            target_user_id=user_id,
                            details={'reason': f"Reached warn limit ({warn_limit})"}
                        )
                except BadRequest as e:
                    message.reply_text(f"Failed to kick user: {e.message}")
            
            elif warn_punishment == 'mute':
                try:
                    until_date = datetime.now() + timedelta(days=1)  # Mute for 1 day
                    context.bot.restrict_chat_member(
                        chat.id, 
                        user_id,
                        until_date=until_date,
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False
                    )
                    message.reply_text(
                        f"User {target_user.first_name} has been muted for 1 day after receiving {warn_limit} warnings."
                    )
                    # Log action
                    if 'logger' in context.bot_data:
                        logger = context.bot_data['logger']
                        logger.log_restrict(
                            group_id=chat.id,
                            admin_id=context.bot.id,
                            user_id=user_id,
                            restrictions={'can_send_messages': False},
                            duration=86400  # 1 day in seconds
                        )
                except BadRequest as e:
                    message.reply_text(f"Failed to mute user: {e.message}")
        else:
            # Just notify about the warning
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Remove Warning", callback_data=f"unwarn_{user_id}")]
            ])
            
            message.reply_text(
                f"User {target_user.first_name} has been warned. ({len(active_warns)}/{warn_limit})\n"
                f"Reason: {reason or 'No reason provided'}",
                reply_markup=keyboard
            )
            
            # Log action
            if 'logger' in context.bot_data:
                logger = context.bot_data['logger']
                logger.log_action(
                    group_id=chat.id,
                    admin_id=admin.id,
                    action_type='warn',
                    target_user_id=user_id,
                    details={'reason': reason or "No reason provided", 'warn_count': len(active_warns)}
                )

def unwarn_user(update: Update, context: CallbackContext) -> None:
    """Remove a warning from a user."""
    chat = update.effective_chat
    admin = update.effective_user
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
            "You must specify a user to remove a warning from. You can reply to a message or provide a username/user ID."
        )
        return
    
    # Get user's warns from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        warns_data = db.get_user_warns(chat.id, user_id) or []
        
        if not warns_data:
            message.reply_text("This user has no warnings to remove.")
            return
        
        # Remove the most recent warning
        warns_data.pop()
        
        # Update database
        db.update_user_warns(chat.id, user_id, warns_data)
        
        # Get user info
        try:
            member = chat.get_member(user_id)
            user_name = member.user.first_name
        except BadRequest:
            user_name = f"User {user_id}"
        
        message.reply_text(
            f"Removed a warning for {user_name}. "
            f"They now have {len(warns_data)} warnings."
        )
        
        # Log action
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_action(
                group_id=chat.id,
                admin_id=admin.id,
                action_type='unwarn',
                target_user_id=user_id,
                details={'warn_count': len(warns_data)}
            )

def unwarn_button(update: Update, context: CallbackContext) -> None:
    """Handle unwarn button callback."""
    query = update.callback_query
    chat = update.effective_chat
    admin = update.effective_user
    
    # Check if user is an admin
    if not is_admin(update, context, admin.id):
        query.answer("You don't have permission to remove warnings.", show_alert=True)
        return
    
    # Extract user ID from callback data
    callback_data = query.data
    prefix = "unwarn_"
    if not callback_data.startswith(prefix):
        return
    
    user_id = int(callback_data[len(prefix):])
    
    # Get user's warns from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        warns_data = db.get_user_warns(chat.id, user_id) or []
        
        if not warns_data:
            query.answer("This user has no warnings to remove.", show_alert=True)
            return
        
        # Remove the most recent warning
        warns_data.pop()
        
        # Update database
        db.update_user_warns(chat.id, user_id, warns_data)
        
        # Get user info
        try:
            member = chat.get_member(user_id)
            user_name = member.user.first_name
        except BadRequest:
            user_name = f"User {user_id}"
        
        # Update message
        query.edit_message_text(
            f"Warning removed by {admin.first_name}. "
            f"{user_name} now has {len(warns_data)} warnings."
        )
        
        # Log action
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_action(
                group_id=chat.id,
                admin_id=admin.id,
                action_type='unwarn',
                target_user_id=user_id,
                details={'warn_count': len(warns_data)}
            )

def reset_warns(update: Update, context: CallbackContext) -> None:
    """Reset all warnings for a user."""
    chat = update.effective_chat
    admin = update.effective_user
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
            "You must specify a user to reset warnings for. You can reply to a message or provide a username/user ID."
        )
        return
    
    # Reset warns in database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        db.clear_user_warns(chat.id, user_id)
        
        # Get user info
        try:
            member = chat.get_member(user_id)
            user_name = member.user.first_name
        except BadRequest:
            user_name = f"User {user_id}"
        
        message.reply_text(f"All warnings for {user_name} have been reset.")
        
        # Log action
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_action(
                group_id=chat.id,
                admin_id=admin.id,
                action_type='resetwarns',
                target_user_id=user_id
            )

def warns(update: Update, context: CallbackContext) -> None:
    """Display warnings for a user."""
    chat = update.effective_chat
    message = update.effective_message
    
    # Check if command is used in a group
    if chat.type not in ['group', 'supergroup']:
        message.reply_text("This command can only be used in groups.")
        return
    
    # Extract user ID from the command
    user_id, _ = extract_user_and_text(update, context)
    
    # If no user specified, default to the message sender
    if not user_id:
        user_id = update.effective_user.id
    
    # Get user's warns from database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        warns_data = db.get_user_warns(chat.id, user_id) or []
        
        # Remove expired warns
        current_time = time.time()
        active_warns = [
            w for w in warns_data 
            if not w.get('expiry') or w.get('expiry', 0) > current_time
        ]
        
        # Update database if some warns were removed due to expiry
        if len(active_warns) < len(warns_data):
            db.update_user_warns(chat.id, user_id, active_warns)
        
        # Get user info
        try:
            member = chat.get_member(user_id)
            user_name = member.user.first_name
        except BadRequest:
            user_name = f"User {user_id}"
        
        # Get config
        config = context.bot_data.get('config', {})
        
        # Get warn settings
        warn_settings = config.get('restrictions', {})
        warn_limit = warn_settings.get('warn_limit', 3)
        
        # Check if group has custom warn settings
        group_data = db.get_group(chat.id)
        if group_data and 'warns' in group_data:
            group_warns = group_data['warns']
            warn_limit = group_warns.get('limit', warn_limit)
        
        if not active_warns:
            message.reply_text(f"{user_name} has no warnings.")
            return
        
        # Format warns list
        warns_text = f"*Warnings for {user_name}*: {len(active_warns)}/{warn_limit}\n\n"
        
        for i, warn in enumerate(active_warns, 1):
            reason = warn.get('reason', "No reason provided")
            admin_id = warn.get('admin_id')
            timestamp = warn.get('timestamp')
            
            # Format admin name
            admin_name = "Unknown"
            if admin_id:
                try:
                    admin = context.bot.get_chat_member(chat.id, admin_id).user
                    admin_name = admin.first_name
                except:
                    admin_name = f"Admin {admin_id}"
            
            # Format timestamp
            time_str = "Unknown time"
            if timestamp:
                warn_time = datetime.fromtimestamp(timestamp)
                time_str = warn_time.strftime("%Y-%m-%d %H:%M:%S")
            
            warns_text += f"*{i}.* Warned by {admin_name} on {time_str}\n"
            warns_text += f"   Reason: {reason}\n\n"
        
        message.reply_text(warns_text, parse_mode=ParseMode.MARKDOWN)

def warnmode(update: Update, context: CallbackContext) -> None:
    """Set warning settings for the group."""
    chat = update.effective_chat
    admin = update.effective_user
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
    if not context.args or len(context.args) < 2:
        # Show current settings
        if 'db' in context.bot_data:
            db = context.bot_data['db']
            group_data = db.get_group(chat.id)
            
            # Get config
            config = context.bot_data.get('config', {})
            
            # Get warn settings
            warn_settings = config.get('restrictions', {})
            warn_limit = warn_settings.get('warn_limit', 3)
            warn_expiry = warn_settings.get('warn_expiry', 604800)  # 7 days in seconds
            warn_punishment = warn_settings.get('warn_punishment', 'ban')
            
            # Check for group-specific settings
            if group_data and 'warns' in group_data:
                group_warns = group_data['warns']
                warn_limit = group_warns.get('limit', warn_limit)
                warn_expiry = group_warns.get('expiry', warn_expiry)
                warn_punishment = group_warns.get('punishment', warn_punishment)
            
            # Format expiry
            if warn_expiry:
                expiry_text = get_readable_time(warn_expiry)
            else:
                expiry_text = "Never (warnings don't expire)"
            
            message.reply_text(
                "Current warn settings:\n"
                f"Warn limit: {warn_limit}\n"
                f"Warn expiry: {expiry_text}\n"
                f"Warn punishment: {warn_punishment.capitalize()}\n\n"
                "To change settings, use:\n"
                "/warnmode limit <number>\n"
                "/warnmode expiry <time in seconds or 'never'>\n"
                "/warnmode punishment <ban/kick/mute>"
            )
        return
    
    # Parse command
    setting = context.args[0].lower()
    value = context.args[1].lower()
    
    if setting not in ['limit', 'expiry', 'punishment']:
        message.reply_text(
            "Invalid setting. Available options: limit, expiry, punishment."
        )
        return
    
    # Validate and parse the value
    if setting == 'limit':
        try:
            limit = int(value)
            if limit < 1:
                message.reply_text("Warn limit must be at least 1.")
                return
            setting_value = limit
        except ValueError:
            message.reply_text("Warn limit must be a number.")
            return
    
    elif setting == 'expiry':
        if value == 'never':
            setting_value = None
        else:
            try:
                expiry = int(value)
                if expiry < 0:
                    message.reply_text("Expiry time cannot be negative.")
                    return
                setting_value = expiry
            except ValueError:
                message.reply_text("Expiry time must be a number of seconds or 'never'.")
                return
    
    elif setting == 'punishment':
        if value not in ['ban', 'kick', 'mute']:
            message.reply_text("Punishment must be one of: ban, kick, mute.")
            return
        setting_value = value
    
    # Update database
    if 'db' in context.bot_data:
        db = context.bot_data['db']
        
        # Update setting in group data
        db.update_group_setting(chat.id, f'warns.{setting}', setting_value)
        
        # Format response message
        if setting == 'limit':
            setting_text = f"Warn limit set to {setting_value} warnings."
        elif setting == 'expiry':
            if setting_value is None:
                setting_text = "Warnings will now never expire."
            else:
                readable_time = get_readable_time(setting_value)
                setting_text = f"Warnings will now expire after {readable_time}."
        else:  # punishment
            setting_text = f"Punishment for reaching warn limit set to: {setting_value}."
        
        message.reply_text(setting_text)
        
        # Log action
        if 'logger' in context.bot_data:
            logger = context.bot_data['logger']
            logger.log_action(
                group_id=chat.id,
                admin_id=admin.id,
                action_type='settings_change',
                details={'setting': f'warns.{setting}', 'value': setting_value}
            )

def register_warns_handlers(
    dispatcher: Dispatcher, 
    config: Dict[str, Any], 
    db: Database, 
    action_logger: ActionLogger
) -> None:
    """Register warning system handlers."""
    # Store config, database and logger reference
    dispatcher.bot_data['config'] = config
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['logger'] = action_logger
    
    # Add database methods if they don't exist
    if not hasattr(db, 'get_user_warns'):
        def get_user_warns(self, group_id: int, user_id: int) -> List[Dict[str, Any]]:
            """Get warnings for a user in a group."""
            group_data = self.get_group(group_id) or {}
            warns_data = group_data.get('user_warns', {})
            return warns_data.get(str(user_id), [])
        
        def update_user_warns(self, group_id: int, user_id: int, warns: List[Dict[str, Any]]) -> None:
            """Update warnings for a user in a group."""
            self.update_group_setting(group_id, f'user_warns.{user_id}', warns)
        
        def clear_user_warns(self, group_id: int, user_id: int) -> None:
            """Clear all warnings for a user in a group."""
            self.update_group_setting(group_id, f'user_warns.{user_id}', [])
        
        # Add methods to Database class
        setattr(Database, 'get_user_warns', get_user_warns)
        setattr(Database, 'update_user_warns', update_user_warns)
        setattr(Database, 'clear_user_warns', clear_user_warns)
    
    # Register command handlers
    dispatcher.add_handler(CommandHandler("warn", warn_user))
    dispatcher.add_handler(CommandHandler("unwarn", unwarn_user))
    dispatcher.add_handler(CommandHandler("resetwarns", reset_warns))
    dispatcher.add_handler(CommandHandler("warns", warns))
    dispatcher.add_handler(CommandHandler("warnmode", warnmode))
    
    # Register callback handlers
    dispatcher.add_handler(CallbackQueryHandler(unwarn_button, pattern=r'^unwarn_'))
    
    logger.info("Warning system handlers registered") 