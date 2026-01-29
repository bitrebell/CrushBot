# CrushBot 🤖

A powerful Telegram bot built with Pyrogram that serves as your personal assistant, monitoring messages, forwarding them to you, and sending offline notifications.

## Features ✨

- **Offline Notifications**: Automatically notifies senders when you're offline
- **Message Forwarding**: Forwards all incoming messages to you with sender information
- **Enable/Disable Functionality**: Easy commands to control bot behavior
- **Direct Message Alerts**: Get notified when someone tries to reach you directly
- **Group Monitoring**: Detects when you or the bot are mentioned in groups
- **Customizable Settings**: Flexible configuration options for your needs
- **Secure**: Only you (the owner) can control the bot
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## Requirements 📋

- Python 3.7 or higher
- A Telegram account
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org/apps))

## Installation 🚀

1. **Clone the repository**
   ```bash
   git clone https://github.com/bitrebell/CrushBot.git
   cd CrushBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   ```env
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   BOT_TOKEN=your_bot_token_here
   OWNER_ID=your_user_id_here
   ```

### Getting Your Credentials 🔑

1. **API_ID and API_HASH**:
   - Visit [my.telegram.org](https://my.telegram.org/apps)
   - Log in with your phone number
   - Create a new application
   - Copy your `api_id` and `api_hash`

2. **BOT_TOKEN**:
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token provided

3. **OWNER_ID**:
   - Search for [@userinfobot](https://t.me/userinfobot) on Telegram
   - Start the bot and it will show your user ID
   - Copy your user ID

## Usage 💡

### Starting the Bot

Run the bot with:
```bash
python bot.py
```

The bot will start and log its status. Keep the terminal running to keep the bot active.

### Available Commands

All commands work only for the bot owner:

- `/start` - Initialize the bot and see welcome message
- `/enable` - Enable bot functionality
- `/disable` - Disable bot (stops notifications and forwarding)
- `/status` - Check current bot status
- `/settings` - View all current settings
- `/setoffline <message>` - Set a custom offline message
- `/help` - Display help information

### Examples

**Enable the bot:**
```
/enable
```

**Set a custom offline message:**
```
/setoffline I'm currently away. I'll respond as soon as I'm back!
```

**Check bot status:**
```
/status
```

**Disable the bot:**
```
/disable
```

## How It Works 🔧

### Private Messages
- When someone sends you a private message, the bot:
  1. Forwards the message to you with sender information
  2. Sends an offline notification to the sender (if enabled)
  3. Logs the interaction

### Group Messages
- **Bot Mentions**: When someone mentions the bot in a group:
  1. Sends offline notification to the group
  2. Forwards the message to you
  
- **Owner Mentions**: When someone mentions you or replies to your message:
  1. Sends you an alert notification
  2. Forwards the message to you

### Enable/Disable
- When disabled, the bot stops all notifications and forwarding
- Settings are preserved when disabled
- Enable again with `/enable` command

## Configuration ⚙️

The bot uses two configuration files:

1. **`.env`**: Environment variables (credentials)
2. **`bot_settings.json`**: Runtime settings (auto-generated)

### Default Settings

```json
{
    "bot_enabled": true,
    "offline_notification": true,
    "forward_messages": true,
    "direct_message_alerts": true,
    "offline_message": "🤖 The user is currently offline. Your message has been forwarded to them."
}
```

Settings are automatically saved and persist across restarts.

## File Structure 📁

```
CrushBot/
├── bot.py                  # Main bot application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── bot_settings.json     # Runtime settings (auto-generated)
├── crushbot.log          # Log file (auto-generated)
└── README.md             # This file
```

## Security 🔒

- **Owner-only control**: Only the configured owner can control the bot
- **Credentials**: Never commit your `.env` file to version control
- **Session files**: Session files are gitignored for security
- **Logging**: Sensitive information is not logged

## Logging 📝

The bot creates two logs:
- **Console output**: Real-time status in terminal
- **crushbot.log**: Persistent log file for debugging

Log entries include timestamps, log levels, and detailed information about bot operations.

## Troubleshooting 🔧

### Bot doesn't start
- Check that all environment variables are set correctly
- Verify your API credentials are valid
- Ensure Python 3.7+ is installed

### Messages not forwarding
- Check if bot is enabled with `/status`
- Verify OWNER_ID is correct
- Check logs for error messages

### Can't control bot
- Ensure you're using the correct Telegram account (matching OWNER_ID)
- Verify BOT_TOKEN is correct
- Try `/start` command

### FloodWait errors
- Telegram has rate limits
- The bot handles this automatically with delays
- Be patient and the bot will retry

## Best Practices 📚

1. **Keep bot running**: Use a process manager like `systemd` or `pm2` for production
2. **Monitor logs**: Regularly check `crushbot.log` for issues
3. **Backup settings**: Keep a backup of your `.env` file securely
4. **Update dependencies**: Regularly update packages for security
5. **Test changes**: Test in a private chat before deploying changes

## Advanced Usage 🚀

### Running as a Service (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/crushbot.service
```

Add:
```ini
[Unit]
Description=CrushBot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/CrushBot
ExecStart=/usr/bin/python3 /path/to/CrushBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable crushbot
sudo systemctl start crushbot
sudo systemctl status crushbot
```

### Running with PM2 (Node.js process manager)

```bash
pm2 start bot.py --name crushbot --interpreter python3
pm2 save
pm2 startup
```

## API Compliance 📜

This bot complies with Telegram's API guidelines:
- Respects rate limits with FloodWait handling
- Uses official Pyrogram library
- Implements proper error handling
- Follows Telegram Bot API best practices

## Data Privacy 🔐

- **No external servers**: All data stays between you and Telegram
- **No data collection**: Bot doesn't store messages permanently
- **Local settings**: Configuration stored locally only
- **Secure credentials**: Environment variables for sensitive data

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is open source and available under the MIT License.

## Support 💬

If you encounter any issues or have questions:
1. Check the logs in `crushbot.log`
2. Review this README
3. Open an issue on GitHub

## Disclaimer ⚠️

This bot is for personal use. Ensure you comply with Telegram's Terms of Service when using automated bots. Use responsibly and respect other users' privacy.

## Acknowledgments 🙏

- Built with [Pyrogram](https://docs.pyrogram.org/)
- Powered by Telegram Bot API

---

Made with ❤️ by bitrebell
