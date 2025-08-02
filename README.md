# Duty Roster Bot

A Telegram bot for managing duty rosters and automatic notifications. This bot helps teams organize duty schedules by automatically rotating through a list of people and sending daily notifications.

## Features

- **Automated Duty Notifications**: Sends daily notifications at 7:45 AM (Yekaterinburg time)
- **Queue Management**: Automatically rotates through the duty list
- **Admin Controls**: Only authorized admin can control the bot
- **Flexible Scheduling**: Configure specific work days for notifications
- **Simple Commands**: Easy-to-use command interface

## Commands

- `/start` - Start the bot and show welcome message
- `/help` - Display available commands
- `/ping` - Check if the bot is alive
- `/next` - Get the next person on duty (and advance the queue)
- `/enable` - Enable automatic notifications
- `/disable` - Disable automatic notifications

## Setup

### Prerequisites

- Python 3.7+
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))
- Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ykengo/Duty-roster-bot.git
   cd Duty-roster-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file with your credentials:
   ```bash
   BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_user_id
   CHAT_ID=target_chat_id_for_notifications
   ```

### Configuration

Edit `list.json` to configure your duty roster:

```json
{
    "list": [
        "John Doe",
        "Jane Smith",
        "Bob Johnson"
    ],
    "queue": 0,
    "enable": true,
    "work_days": [0, 1, 2, 3, 4]
}
```

- `list`: Array of people in the duty roster
- `queue`: Current position in the queue (0-indexed)
- `enable`: Whether automatic notifications are enabled
- `work_days`: Days of the week for notifications (0=Monday, 6=Sunday)

## Usage

1. Start the bot:
   ```bash
   python bot.py
   ```

2. Send `/start` to your bot in Telegram

3. Use `/enable` to start automatic notifications

4. The bot will send daily notifications at 7:45 AM on configured work days

## How It Works

1. **Daily Notifications**: The bot uses APScheduler to send notifications at 7:45 AM
2. **Queue Management**: Each time a duty is assigned, the queue advances to the next person
3. **Work Days**: Only sends notifications on configured work days
4. **Admin Only**: Only the configured admin can use bot commands

## Dependencies

- **aiogram**: Telegram Bot API framework
- **python-dotenv**: Environment variable management
- **APScheduler**: Task scheduling
- **python-dateutil**: Date utilities
- **pytz**: Timezone handling


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

If you encounter any issues or have questions, please create an issue on GitHub.