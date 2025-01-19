"""
Duty Roster Bot
--------------
A Telegram bot that manages duty roster schedule and notifications.
Features:
- Daily notifications about who is on duty
- Manual duty rotation with /next command
- Health check with /ping command
- Automatic duty rotation on workdays
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, List

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Bot configuration constants
ADMIN_CHAT_ID = admin id here  # Admin's personal chat ID for management commands
GROUP_CHAT_ID = group id here # Group chat ID for duty notifications
DUTY_FILE = 'spisok.json'  # JSON file storing duty roster data
WORK_DAYS = {0, 2, 3, 4, 5}  # Workdays: Monday=0, Wednesday=2, Thursday=3, etc
NOTIFICATION_HOUR = 5  # Hour to send daily notification (24h format)
NOTIFICATION_MINUTE = "45"  # Minute to send daily notification

# Initialize environment and router
load_dotenv()  # Load environment variables from .env file
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

hello_router = Router(name='hello')  # Router for handling bot commands

class DutyData:
    """Manages duty roster data persistence and state"""
    def __init__(self, filepath: str):
        """Initialize with JSON file path containing duty data"""
        self.filepath = filepath
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load duty roster data from JSON file"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def save_data(self):
        """Save duty roster data with thread safety"""
        async with asyncio.Lock():  # Prevent concurrent writes
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)

# Initialize duty data
duty_data = DutyData(DUTY_FILE)
spisok = duty_data.data['list']  # List of people on duty

class SchedulerMiddleware(BaseMiddleware):
    """Middleware to inject scheduler instance into handlers"""
    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self._scheduler = scheduler

    async def __call__(self, handler, event, data):
        """Pass scheduler to event handlers"""
        data["scheduler"] = self._scheduler
        return await handler(event, data)

async def is_workday() -> bool:
    """Check if current day is a workday"""
    return datetime.now().weekday() in WORK_DAYS

async def send_duty_notification(bot: Bot):
    """Send duty notification and rotate duty roster"""
    if await is_workday():
        # Prepare and send notification
        message = f"Дежурные: {spisok[duty_data.data['n']]}"
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
        
        # Rotate to next person on duty
        if duty_data.data['n'] != len(spisok):
            duty_data.data['n'] += 1
        else:
            duty_data.data['n'] = 0
        await duty_data.save_data()

@hello_router.message(Command(commands=["next"]))
async def next(message: Message, bot: Bot):
    """Handle manual duty rotation command"""
    if message.chat.id == ADMIN_CHAT_ID and await is_workday():
        await send_duty_notification(bot)

@hello_router.message(Command(commands=["ping"]))
async def ping(message: Message, bot: Bot, scheduler: AsyncIOScheduler):
    """Health check command"""
    await message.answer(text="pong")

async def main():
    """Initialize and start the bot"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    )
    
    # Initialize scheduler with Moscow timezone
    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()
    
    # Setup bot and dispatcher
    bot = Bot(TOKEN)
    dp = Dispatcher()
    
    # Configure middleware and routes
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
    dp.include_routers(hello_router)
    
    # Schedule daily duty notification
    scheduler.add_job(
        send_duty_notification, 
        'cron', 
        hour=NOTIFICATION_HOUR, 
        minute=NOTIFICATION_MINUTE,
        args=[bot]
    )
    
    # Start bot with error handling
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot stopped due to error: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())