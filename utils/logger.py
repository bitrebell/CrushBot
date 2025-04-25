"""
Logger utility for CrushBot
Handles logging of actions for auditing purposes
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from utils.database import Database

logger = logging.getLogger(__name__)

class ActionLogger:
    """Logs actions taken by users and admins."""
    
    # Action types
    ACTION_BAN = 'ban'
    ACTION_UNBAN = 'unban'
    ACTION_RESTRICT = 'restrict'
    ACTION_WARN = 'warn'
    ACTION_MUTE = 'mute'
    ACTION_UNMUTE = 'unmute'
    ACTION_WELCOME_SET = 'welcome_set'
    ACTION_SETTINGS_CHANGE = 'settings_change'
    
    def __init__(self, db: Database):
        """Initialize the action logger."""
        self.db = db
    
    def log_action(self, 
                   group_id: int,
                   admin_id: int,
                   action_type: str,
                   target_user_id: Optional[int] = None,
                   details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an action taken by an admin.
        
        Args:
            group_id: The ID of the group where the action occurred
            admin_id: The ID of the admin who performed the action
            action_type: The type of action (from class constants)
            target_user_id: The ID of the user targeted by the action (if applicable)
            details: Additional details about the action
        """
        log_data = {
            'group_id': group_id,
            'admin_id': admin_id,
            'action_type': action_type,
            'timestamp': datetime.now()
        }
        
        if target_user_id:
            log_data['target_user_id'] = target_user_id
            
        if details:
            log_data['details'] = details
            
        try:
            self.db.add_log(log_data)
            logger.info(f"Action logged: {action_type} by {admin_id} in group {group_id}")
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
    
    def log_ban(self, 
               group_id: int,
               admin_id: int,
               user_id: int,
               reason: Optional[str] = None,
               duration: Optional[int] = None) -> None:
        """Log a ban action."""
        details = {'reason': reason}
        if duration:
            details['duration'] = duration
            
        self.log_action(
            group_id=group_id,
            admin_id=admin_id,
            action_type=self.ACTION_BAN,
            target_user_id=user_id,
            details=details
        )
    
    def log_unban(self,
                 group_id: int,
                 admin_id: int,
                 user_id: int) -> None:
        """Log an unban action."""
        self.log_action(
            group_id=group_id,
            admin_id=admin_id,
            action_type=self.ACTION_UNBAN,
            target_user_id=user_id
        )
    
    def log_restrict(self,
                    group_id: int,
                    admin_id: int,
                    user_id: int,
                    restrictions: Dict[str, bool],
                    duration: Optional[int] = None) -> None:
        """Log a restriction action."""
        details = {'restrictions': restrictions}
        if duration:
            details['duration'] = duration
            
        self.log_action(
            group_id=group_id,
            admin_id=admin_id,
            action_type=self.ACTION_RESTRICT,
            target_user_id=user_id,
            details=details
        )
    
    def log_welcome_set(self,
                       group_id: int,
                       admin_id: int,
                       welcome_message: str) -> None:
        """Log when welcome message is set or changed."""
        self.log_action(
            group_id=group_id,
            admin_id=admin_id,
            action_type=self.ACTION_WELCOME_SET,
            details={'message': welcome_message}
        ) 