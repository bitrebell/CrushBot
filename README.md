# 🤖 CrushBot - Advanced Telegram Userbot

CrushBot is a powerful and feature-rich Telegram userbot built with Pyrogram. It offers a wide range of commands for text manipulation, utilities, entertainment, and advanced features.

## ✨ Features

### 🔧 Basic Commands
- `.help` - Show all available commands
- `.ping` - Check bot latency  
- `.info` - Get user/chat information
- `.id` - Get user/chat ID
- `.sys` - System information
- `.uptime` - Bot uptime
- `.logs` - Get recent logs
- `.restart` - Restart the bot

### 📝 Text Commands
- `.type <text>` - Typewriter effect
- `.reverse <text>` - Reverse text
- `.upper <text>` - Convert to uppercase
- `.lower <text>` - Convert to lowercase
- `.title <text>` - Convert to title case
- `.count <text>` - Count characters/words
- `.mock <text>` - Mocking SpongeBob case
- `.fancy <text>` - Fancy text formatting
- `.bubble <text>` - Bubble letters
- `.zalgo <text>` - Zalgo text effect
- `.emoji <text>` - Convert to emoji letters
- `.replace <old> <new> <text>` - Replace text

### 🎭 Fun Commands
- `.dice` - Roll a dice
- `.coin` - Flip a coin
- `.8ball <question>` - Magic 8-ball
- `.random [max] [min max]` - Generate random numbers
- `.choose <option1> <option2> ...` - Choose randomly
- `.slots` - Slot machine game
- `.roll [sides] [XdY]` - Advanced dice rolling
- `.fortune` - Fortune cookie messages

### 🌐 Utility Commands
- `.weather <city>` - Get weather information
- `.qr <text>` - Generate QR code
- `.shorturl <url>` - Shorten URLs
- `.speed` - Internet speed test
- `.time` - Current time and date
- `.calc <expression>` - Calculator
- `.base64 <encode/decode> <text>` - Base64 operations
- `.hash <md5/sha1/sha256> <text>` - Generate hashes

### ⚡ Advanced Commands
- `.spam <count> <text>` - Spam messages (use responsibly)
- `.purge` - Delete messages in bulk
- `.auto_react [add/remove]` - Auto react to messages
- `.translate <lang> <text>` - Translate text
- `.youtube <query>` - Search YouTube
- `.ascii <text>` - ASCII art
- `.math <operation> <numbers>` - Advanced math operations

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Telegram API credentials (API_ID and API_HASH)

### Step 1: Clone and Setup
```bash
git clone <repository_url>
cd CrushBot
pip install -r requirements.txt
```

### Step 2: Configuration
1. Copy `.env.example` to `.env`
2. Edit `.env` with your credentials:

```env
# Required - Get from https://my.telegram.org
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number

# Optional - For advanced features
WEATHER_API_KEY=your_openweather_api_key
YOUTUBE_API_KEY=your_youtube_api_key
ADMIN_ID=your_telegram_user_id
```

### Step 3: Getting API Credentials

#### Telegram API
1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy API_ID and API_HASH

#### Weather API (Optional)
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key from the dashboard

### Step 4: Run the Bot
```bash
python main.py
```

On first run, you'll be prompted to enter your phone verification code.

## 📁 Project Structure

```
CrushBot/
├── main.py                 # Main bot file
├── requirements.txt        # Python dependencies
├── .env                   # Configuration file
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── helpers.py         # Helper functions
│   └── formatters.py      # Text formatting utilities
├── plugins/               # Command plugins
│   ├── __init__.py
│   ├── basic_commands.py  # Basic commands
│   ├── text_commands.py   # Text manipulation
│   ├── fun_commands.py    # Entertainment commands
│   ├── utility_commands.py # Utility commands
│   └── advanced_commands.py # Advanced features
└── README.md             # This file
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| API_ID | Yes | Telegram API ID |
| API_HASH | Yes | Telegram API Hash |
| PHONE_NUMBER | Yes | Your phone number |
| SESSION_STRING | No | Session string (alternative to phone login) |
| WEATHER_API_KEY | No | OpenWeatherMap API key |
| YOUTUBE_API_KEY | No | YouTube Data API key |
| ADMIN_ID | No | Your Telegram user ID |

## 🛡️ Security & Safety

### Important Notes
- **Use responsibly**: Some commands like `.spam` and `.purge` can be disruptive
- **Rate limiting**: The bot includes built-in delays to avoid Telegram flood limits
- **Privacy**: Never share your API credentials or session files
- **Backups**: Keep backups of your session files to avoid re-authentication

### Safety Features
- Maximum limits on spam and purge operations
- Automatic flood wait handling
- Error logging and recovery
- Input validation and sanitization

## 🔌 Plugin System

CrushBot uses a modular plugin system. Each plugin file in the `plugins/` directory is automatically loaded.

### Creating Custom Plugins

Create a new file in `plugins/` directory:

```python
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("mycommand", prefixes="."))
async def my_command(client: Client, message: Message):
    """My custom command"""
    await message.edit_text("Hello from my custom command!")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## ⚠️ Disclaimer

This userbot is for educational and personal use only. Users are responsible for complying with Telegram's Terms of Service and local laws. The developers are not responsible for any misuse of this software.

## 🐛 Troubleshooting

### Common Issues

1. **"API_ID and API_HASH are required!"**
   - Make sure your `.env` file is properly configured

2. **"Phone number invalid"**
   - Include country code (e.g., +1234567890)

3. **"Module not found" errors**
   - Run `pip install -r requirements.txt`

4. **Connection errors**
   - Check your internet connection
   - Verify API credentials

### Getting Help

- Check the logs: `tail -f userbot.log`
- Use `.logs` command to see recent errors
- Make sure all dependencies are installed

## 🌟 Features in Development

- [ ] Media manipulation commands
- [ ] Voice message support
- [ ] Database integration
- [ ] Web dashboard
- [ ] Custom themes
- [ ] Plugin marketplace

---

**Made with ❤️ by GitHub Copilot**
