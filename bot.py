#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CrushBot - A Telegram bot for advanced group management
"""

import logging
import yaml
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ParseMode

# Import modules
from handlers.user_management import register_user_management_handlers
from handlers.welcome import register_welcome_handlers
from handlers.admin_commands import register_admin_handlers
from handlers.general_commands import register_general_handlers
from handlers.antiflood import register_antiflood_handlers
from handlers.blacklist import register_blacklist_handlers
from handlers.warns import register_warns_handlers
from utils.database import Database
from utils.logger import ActionLogger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        if not os.path.exists(config_path):
            logger.error(f"Config file {config_path} not found. Please create it from config.example.yaml.")
        exit(1)

def main():
    """Start the bot."""
    # Load configuration
    config = load_config()
    
    # Setup database connection
    db = Database(config['database']['uri'], config['database']['name'])
    
    # Initialize action logger
    action_logger = ActionLogger(db)
    
    # Create the Updater and pass it your bot's token
    updater = Updater(config['bot']['token'])
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Register all command handlers
    register_general_handlers(dispatcher, config)
    register_user_management_handlers(dispatcher, config, db, action_logger)
    register_welcome_handlers(dispatcher, config, db)
    register_admin_handlers(dispatcher, config, db, action_logger)
    
    # Register new handlers for expanded functionality
    register_antiflood_handlers(dispatcher, config, db)
    register_blacklist_handlers(dispatcher, config, db)
    register_warns_handlers(dispatcher, config, db, action_logger)
    
    # Start the Bot
    updater.start_polling()
    logger.info(f"{config['bot']['name']} started. Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main() 