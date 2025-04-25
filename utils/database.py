"""
Database utility for CrushBot
Handles all database operations
"""

import logging
import pymongo
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class Database:
    """Database handler for the bot."""
    
    def __init__(self, uri: str, db_name: str):
        """Initialize database connection."""
        try:
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[db_name]
            # Create collections if they don't exist
            self.users = self.db.users
            self.groups = self.db.groups
            self.banned_users = self.db.banned_users
            self.logs = self.db.logs
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def add_user(self, user_id: int, user_data: Dict[str, Any]) -> None:
        """Add or update a user in the database."""
        user_data['updated_at'] = datetime.now()
        self.users.update_one(
            {'user_id': user_id}, 
            {'$set': user_data}, 
            upsert=True
        )
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database."""
        return self.users.find_one({'user_id': user_id})
    
    def add_group(self, group_id: int, group_data: Dict[str, Any]) -> None:
        """Add or update a group in the database."""
        group_data['updated_at'] = datetime.now()
        self.groups.update_one(
            {'group_id': group_id}, 
            {'$set': group_data}, 
            upsert=True
        )
    
    def get_group(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get group data from database."""
        return self.groups.find_one({'group_id': group_id})
    
    def update_group_setting(self, group_id: int, setting: str, value: Any) -> None:
        """Update a specific group setting."""
        self.groups.update_one(
            {'group_id': group_id},
            {'$set': {setting: value, 'updated_at': datetime.now()}},
            upsert=True
        )
    
    def ban_user(self, group_id: int, user_id: int, ban_data: Dict[str, Any]) -> None:
        """Add a user to the ban list."""
        ban_data['group_id'] = group_id
        ban_data['user_id'] = user_id
        ban_data['created_at'] = datetime.now()
        self.banned_users.update_one(
            {'group_id': group_id, 'user_id': user_id},
            {'$set': ban_data},
            upsert=True
        )
    
    def unban_user(self, group_id: int, user_id: int) -> None:
        """Remove a user from the ban list."""
        self.banned_users.delete_one({'group_id': group_id, 'user_id': user_id})
    
    def get_banned_user(self, group_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a banned user's information."""
        return self.banned_users.find_one({'group_id': group_id, 'user_id': user_id})
    
    def get_banned_users(self, group_id: int) -> List[Dict[str, Any]]:
        """Get all banned users for a group."""
        return list(self.banned_users.find({'group_id': group_id}))
    
    def add_log(self, log_data: Dict[str, Any]) -> None:
        """Add a log entry."""
        log_data['timestamp'] = datetime.now()
        self.logs.insert_one(log_data)
    
    def get_logs(self, group_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get logs for a specific group."""
        return list(self.logs.find(
            {'group_id': group_id}).sort('timestamp', -1).limit(limit)
        )
    
    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Database connection closed") 