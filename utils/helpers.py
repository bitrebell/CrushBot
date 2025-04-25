"""
Helper functions for CrushBot
Contains utility functions used across the bot
"""

import logging
import re
import functools
from datetime import datetime, timedelta
from typing import Tuple, Optional, Union, Dict, Any, Callable
from telegram import Update, User, Chat
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Regular expression patterns for parsing command arguments
DURATION_PATTERN = re.compile(r'(\d+)([mhdw])')
USER_MENTION_PATTERN = re.compile(r'@([a-zA-Z][a-zA-Z0-9_]{4,31})')

# Caches for expensive operations
admin_cache = {}  # Format: {(chat_id, user_id): (is_admin, expiry_time)}
ADMIN_CACHE_TTL = 300  # 5 minutes

# Pre-calculated time multipliers
TIME_MULTIPLIERS = {
    'm': 60,        # minute
    'h': 3600,      # hour
    'd': 86400,     # day
    'w': 604800     # week
}

# Function to cache user IDs from username
def update_username_cache(context: CallbackContext, username: str, user_id: int) -> None:
    """Update the username to user_id cache."""
    if not context.bot_data.get('username_cache'):
        context.bot_data['username_cache'] = {}
    context.bot_data['username_cache'][username] = user_id

def extract_user_and_text(update: Update, context: CallbackContext) -> Tuple[Optional[int], str]:
    """
    Extract user ID and text from a command.
    Works with username, user ID, or reply.
    
    Returns:
        Tuple containing (user_id, remaining_text)
    """
    message = update.effective_message
    user_id = None
    text = ""
    
    # First check if message is a reply
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        # Also update the username cache
        if message.reply_to_message.from_user.username:
            update_username_cache(
                context, 
                message.reply_to_message.from_user.username,
                user_id
            )
        
        if message.text:
            text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ""
    else:
        # Check if there are arguments
        if not message.text or len(message.text.split()) <= 1:
            return None, ""
            
        args = message.text.split(' ', 2)
        
        # Check if first argument is a username
        if args[1].startswith('@'):
            username = args[1][1:]
            # Try to get user from username (if bot has seen this user before)
            if not context.bot_data.get('username_cache'):
                context.bot_data['username_cache'] = {}
            
            if username in context.bot_data['username_cache']:
                user_id = context.bot_data['username_cache'][username]
            else:
                # Try to get user from chat members if in a group
                if update.effective_chat.type in ['group', 'supergroup']:
                    try:
                        members = context.bot.get_chat_administrators(update.effective_chat.id)
                        for member in members:
                            if member.user.username == username:
                                user_id = member.user.id
                                # Update cache
                                update_username_cache(context, username, user_id)
                                break
                    except Exception as e:
                        logger.warning(f"Error getting chat administrators: {e}")
                
        # Check if first argument is a user ID
        elif args[1].isdigit():
            user_id = int(args[1])
            
        # Get remaining text
        if len(args) > 2:
            text = args[2]
            
    return user_id, text

def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse a duration string (e.g., '1h', '30m', '2d') to seconds.
    
    Args:
        duration_str: String representation of duration
        
    Returns:
        Duration in seconds or None if invalid format
    """
    if not duration_str:
        return None
        
    match = DURATION_PATTERN.match(duration_str)
    if not match:
        return None
        
    value, unit = match.groups()
    value = int(value)
    
    # Use pre-calculated multipliers
    return value * TIME_MULTIPLIERS.get(unit, 0)

def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to a human-readable time format.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Human-readable time string
    """
    if seconds <= 0:
        return "0 seconds"
        
    intervals = (
        ('weeks', 604800),  # 60 * 60 * 24 * 7
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )
    
    result = []
    
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append(f"{value} {name}")
            
    return ', '.join(result)

def is_admin(update: Update, context: CallbackContext, user_id: Optional[int] = None) -> bool:
    """
    Check if a user is an admin in the current chat or is a bot admin.
    Uses caching to avoid repeated API calls.
    
    Args:
        update: The update object
        context: The context object
        user_id: The user ID to check (defaults to user who sent the message)
        
    Returns:
        True if user is an admin, False otherwise
    """
    if not user_id:
        user_id = update.effective_user.id
        
    # Check if user is a bot admin (from config)
    if 'admins' in context.bot_data and user_id in context.bot_data['admins']:
        return True
        
    # Check if user is a chat admin
    chat = update.effective_chat
    if chat.type not in ['group', 'supergroup']:
        return False
    
    # Check cache first
    cache_key = (chat.id, user_id)
    now = datetime.now().timestamp()
    
    if cache_key in admin_cache:
        is_admin_status, expiry = admin_cache[cache_key]
        if now < expiry:
            return is_admin_status
    
    # Not in cache or expired, check with API
    try:
        member = chat.get_member(user_id)
        is_admin_status = member.status in ['creator', 'administrator']
        
        # Cache the result
        admin_cache[cache_key] = (is_admin_status, now + ADMIN_CACHE_TTL)
        
        return is_admin_status
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False 