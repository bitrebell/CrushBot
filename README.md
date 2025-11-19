# 🤖 CrushBot - YouTube Downloader Bot

A powerful Telegram bot built with Pyrogram that allows you to download YouTube videos in both audio (MP3) and video (MP4) formats.

## ✨ Features

- 🎵 Download YouTube videos as MP3 audio files
- 🎬 Download YouTube videos as MP4 video files
- 📱 Easy-to-use inline keyboard interface
- 🚀 Fast and reliable downloads using yt-dlp
- 📊 Real-time download progress updates
- 🎯 Supports all YouTube video URLs

## 📋 Requirements

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Telegram API ID and API Hash (from [my.telegram.org](https://my.telegram.org))
- FFmpeg (for audio conversion)

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bitrebell/CrushBot.git
   cd CrushBot
   ```

2. **Install FFmpeg:**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **On macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **On Windows:**
   Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your credentials:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   ```

5. **Set up YouTube cookies (REQUIRED):**
   
   YouTube requires authentication to download videos. You need to provide cookies:
   
   ```bash
   chmod +x setup_cookies.sh
   ./setup_cookies.sh
   ```
   
   Follow the instructions to export cookies from your browser. See [COOKIES_SETUP.md](COOKIES_SETUP.md) for detailed guide.

## 🚀 Getting Telegram Credentials

### 1. Get Bot Token:
- Open Telegram and search for [@BotFather](https://t.me/botfather)
- Send `/newbot` command
- Follow the instructions to create your bot
- Copy the bot token

### 2. Get API ID and API Hash:
- Go to [my.telegram.org](https://my.telegram.org)
- Log in with your phone number
- Click on "API development tools"
- Create a new application
- Copy `api_id` and `api_hash`

## 💻 Usage

1. **Start the bot:**
   ```bash
   python bot.py
   ```

2. **In Telegram:**
   - Start a chat with your bot
   - Send `/start` to see welcome message
   - Send a YouTube video link
   - Choose between Audio (MP3) or Video (MP4) format
   - Wait for the download and receive your file!

## 📝 Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information and usage instructions

## 📁 Project Structure

```
CrushBot/
├── bot.py              # Main bot file with Pyrogram handlers
├── downloader.py       # YouTube download functionality using yt-dlp
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## 🛠️ How It Works

1. User sends a YouTube link to the bot
2. Bot presents inline keyboard with Audio/Video options
3. User selects preferred format
4. Bot downloads the content using yt-dlp
5. Bot uploads the file back to the user
6. Temporary files are automatically cleaned up

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your API credentials secure
- The `.gitignore` file is configured to exclude sensitive files

## 📦 Dependencies

- **pyrogram** - Telegram MTProto API framework
- **tgcrypto** - Cryptography library for Pyrogram (speeds up encryption)
- **yt-dlp** - YouTube video/audio downloader
- **python-dotenv** - Environment variable management

## ⚠️ Limitations

- File size limit depends on your Telegram account type:
  - Regular bots: 50 MB
  - Premium users: 2 GB (when using bot as user)
- Download time depends on video size and internet speed
- Some videos may be geo-restricted or unavailable

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing

## 💬 Support

If you encounter any issues or have questions:
1. Check the `/help` command in the bot
2. Review this README
3. Open an issue on GitHub

---

**Made with ❤️ using Pyrogram and yt-dlp**
