#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CrushBot - A Telegram bot for advanced group management
"""

import logging
import yaml
import os
import time
import functools
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ParseMode, Bot, TelegramError
from telegram.utils.request import Request

# Import modules
from handlers.user_management import register_user_management_handlers
from handlers.welcome import register_welcome_handlers
from handlers.admin_commands import register_admin_handlers
from handlers.general_commands import register_general_handlers
from utils.database import Database
from utils.logger import ActionLogger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create a cache for frequently accessed data
cache = {}

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    try:
        # Check if config is already cached
        if 'config' in cache:
            return cache['config']
            
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            # Cache the config
            cache['config'] = config
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        if not os.path.exists(config_path):
            logger.error(f"Config file {config_path} not found. Please create it from config.example.yaml.")
        exit(1)

def main():
    """Start the bot."""
    start_time = time.time()
    
    # Load configuration
    config = load_config()
    
    # Setup database connection
    db = Database(config['database']['uri'], config['database']['name'])
    
    # Initialize action logger
    action_logger = ActionLogger(db)
    
    # Configure custom connection pool for better performance
    request = Request(con_pool_size=16, connect_timeout=15.0, read_timeout=15.0)
    
    # Create the bot with custom request
    bot = Bot(token=config['bot']['token'], request=request)
    
    # Create the Updater with custom settings
    updater = Updater(bot=bot, workers=8)  # Increase number of worker threads
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # Store common objects in dispatcher for easy access
    dispatcher.bot_data['config'] = config
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['logger'] = action_logger
    
    # Preload username cache for faster user lookups
    dispatcher.bot_data['username_cache'] = {}
    
    # Register all command handlers
    register_general_handlers(dispatcher, config)
    register_user_management_handlers(dispatcher, config, db, action_logger)
    register_welcome_handlers(dispatcher, config, db)
    register_admin_handlers(dispatcher, config, db, action_logger)
    
    # Log startup time
    startup_time = time.time() - start_time
    logger.info(f"Startup completed in {startup_time:.2f} seconds")
    
    # Start the Bot
    updater.start_polling(timeout=30, drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    logger.info(f"{config['bot']['name']} started. Press Ctrl+C to stop.")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main() 