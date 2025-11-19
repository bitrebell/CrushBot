# CrushBot 🎵

A Python Telegram bot for playing music in voice chats from Spotify.

## Features

✨ **Key Features:**
- 🔍 Search for songs on Spotify
- ▶️ Play music in Telegram voice chats
- 🎵 High-quality audio streaming
- 📋 Display track information (artist, album, duration)
- 🔗 Support for Spotify track links
- 💬 Interactive inline buttons for easy playback

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8 or higher** installed
2. **FFmpeg** - Required for audio processing
3. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather)
4. **Spotify API Credentials** - Get them from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

## Installation

### 1. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 2. Clone the repository

```bash
git clone https://github.com/bitrebell/CrushBot.git
cd CrushBot
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Optional: Download directory
DOWNLOAD_DIR=./downloads
```

## Getting API Credentials

### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided by BotFather
5. Paste it in your `.env` file as `TELEGRAM_BOT_TOKEN`

### Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Once created, you'll see your **Client ID** and **Client Secret**
6. Copy both and paste them in your `.env` file

## Usage

### Start the bot

```bash
python bot.py
```

### Bot Commands

Once the bot is running, you can interact with it on Telegram:

- `/start` - Display welcome message
- `/help` - Show help information
- `/search <song name>` - Search for songs
- Send any text - Will be treated as a search query
- Send a Spotify track link - Get track info and download option

### Examples

**Search for a song:**
```
/search Bohemian Rhapsody
```
or simply send:
```
Bohemian Rhapsody Queen
```

**Use Spotify link:**
```
https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv
```

## Project Structure

```
CrushBot/
├── bot.py                 # Main bot application
├── spotify_handler.py     # Spotify integration and download logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── .gitignore           # Git ignore rules
├── downloads/           # Downloaded music files (auto-created)
└── README.md           # This file
```

## How It Works

1. **Search**: The bot uses Spotify's API to search for tracks
2. **Display**: Results are shown with inline buttons
3. **Download**: When you click download, the bot uses `spotdl` to fetch the audio from YouTube
4. **Upload**: The downloaded file is sent to you as a Telegram audio message
5. **Cleanup**: Downloaded files are automatically deleted after sending

## Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- `spotipy` - Spotify Web API wrapper
- `spotdl` - Download songs from Spotify (via YouTube)
- `python-dotenv` - Environment variable management
- `pydub` - Audio processing
- `requests` - HTTP library

## Troubleshooting

### Bot doesn't respond
- Check if your `TELEGRAM_BOT_TOKEN` is correct
- Ensure the bot is running (`python bot.py`)
- Check the console for error messages

### Downloads fail
- Verify your Spotify API credentials are correct
- Check your internet connection
- Some songs may not be available for download

### "TELEGRAM_BOT_TOKEN not found" error
- Make sure you created the `.env` file
- Verify the `.env` file is in the same directory as `bot.py`
- Check that the variable name is exactly `TELEGRAM_BOT_TOKEN`

## Notes

- Downloaded music is temporarily stored in the `downloads/` directory
- Files are automatically deleted after being sent to maintain disk space
- The bot downloads audio from YouTube based on Spotify metadata
- Download quality depends on source availability

## Legal Notice

This bot is for educational purposes only. Please ensure you comply with:
- Spotify's Terms of Service
- YouTube's Terms of Service
- Copyright laws in your jurisdiction
- Only download music you have the right to access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/bitrebell/CrushBot/issues) page
2. Create a new issue if your problem isn't already listed
3. Provide as much detail as possible (error messages, logs, etc.)

## Author

**bitrebell**
- GitHub: [@bitrebell](https://github.com/bitrebell)

---

⭐ If you find this project useful, please consider giving it a star!
