# Duty Roster Bot

A Telegram bot for managing duty roster schedules in group chats. Automatically notifies about daily duties and supports manual rotation commands.

## Features

- Daily duty notifications at configured time
- Manual duty rotation with commands
- Workday-only notifications
- Admin controls for roster management
- Health check monitoring

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/duty-roster-bot
cd duty-roster-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure bot token in .env file and duty roster in spisok.json

Configuration:
  - ADMIN_CHAT_ID: Telegram chat ID for admin commands
  - GROUP_CHAT_ID: Target group for notifications
  - WORK_DAYS: Set of workdays (0=Monday, 6=Sunday)
  - NOTIFICATION_HOUR: Hour for daily notifications (24h format)
  - NOTIFICATION_MINUTE: Minute for daily notifications

Commands:
  - /next - Manually rotate to next person (admin only)
  - /ping - Check if bot is running

Dependencies:
  - Python 3.8+
  - aiogram 3
  - APScheduler
  - python-dotenv

Deployment:
  - Run the bot:
    ```
    python bot.py
    ```
  - For production, consider using systemd service or Docker.
