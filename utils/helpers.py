"""
Helper functions for CrushBot
Contains utility functions used across the bot
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, Union, Dict, Any
from telegram import Update, User, Chat
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Regular expression patterns for parsing command arguments
DURATION_PATTERN = re.compile(r'(\d+)([mhdw])')
USER_MENTION_PATTERN = re.compile(r'@([a-zA-Z][a-zA-Z0-9_]{4,31})')

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
                # User not found in cache, we'll have to handle this error upstream
                pass
                
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
    
    if unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    elif unit == 'w':
        return value * 604800
    else:
        return None

def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to a human-readable time format.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Human-readable time string
    """
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
            
    return ', '.join(result) if result else "0 seconds"

def is_admin(update: Update, context: CallbackContext, user_id: Optional[int] = None) -> bool:
    """
    Check if a user is an admin in the current chat or is a bot admin.
    
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
        
    member = chat.get_member(user_id)
    return member.status in ['creator', 'administrator'] 