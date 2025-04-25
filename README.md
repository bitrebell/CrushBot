# CrushBot - Telegram Group Management Bot

A powerful Telegram bot designed for advanced group management.

## Features

- **User Management**: Ban and restrict users temporarily or permanently
- **Welcome Messages**: Customizable welcome messages for new members
- **Admin Commands**: View banned users, unban users, and manage restrictions
- **Logging**: Track user actions and moderation events

## Setup Instructions

1. **Prerequisites**:
   - Python 3.7+
   - pip (Python package manager)

2. **Installation**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/CrushBot.git
   cd CrushBot
   
   # Create a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**:
   - Create a new bot with [@BotFather](https://t.me/BotFather) on Telegram
   - Copy your API token
   - Rename `config.example.yaml` to `config.yaml`
   - Update the configuration file with your bot token and admin IDs

4. **Running the Bot**:
   ```bash
   python bot.py
   ```

## Usage

### Admin Commands

- `/ban <username/id> [duration] [reason]` - Ban a user
- `/unban <username/id>` - Unban a user
- `/restrict <username/id> [restrictions]` - Restrict a user's actions
- `/banlist` - View list of banned users
- `/setwelcome <message>` - Set a custom welcome message
- `/logs [number]` - View recent moderation logs

### User Commands

- `/start` - Get information about the bot
- `/help` - View available commands
- `/rules` - Display group rules

## Testing

Run the test suite to ensure everything works correctly:
```bash
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 