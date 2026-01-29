"""
Configuration management for CrushBot
"""
import os
import json
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for bot settings"""
    
    # Telegram API credentials
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    
    # Bot settings file
    SETTINGS_FILE = "bot_settings.json"
    
    # Default settings
    DEFAULT_SETTINGS = {
        "bot_enabled": True,
        "offline_notification": True,
        "forward_messages": True,
        "direct_message_alerts": True,
        "offline_message": "🤖 The user is currently offline. Your message has been forwarded to them."
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.API_ID or not cls.API_HASH or not cls.BOT_TOKEN:
            return False
        if not cls.OWNER_ID or cls.OWNER_ID == 0:
            return False
        return True
    
    @classmethod
    def get_required_vars(cls) -> list:
        """Get list of required environment variables"""
        return ["API_ID", "API_HASH", "BOT_TOKEN", "OWNER_ID"]


class Settings:
    """Manage bot runtime settings"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or Config.SETTINGS_FILE
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return Config.DEFAULT_SETTINGS.copy()
        return Config.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a setting value and save"""
        self.settings[key] = value
        return self.save_settings()
    
    def is_enabled(self) -> bool:
        """Check if bot is enabled"""
        return self.settings.get("bot_enabled", True)
    
    def enable(self) -> bool:
        """Enable the bot"""
        return self.set("bot_enabled", True)
    
    def disable(self) -> bool:
        """Disable the bot"""
        return self.set("bot_enabled", False)
    
    def get_offline_message(self) -> str:
        """Get the offline notification message"""
        return self.settings.get("offline_message", Config.DEFAULT_SETTINGS["offline_message"])
