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

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
CHAT_ID = os.getenv("CHAT_ID")


bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Yekaterinburg")


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if event.from_user.id != int(ADMIN_ID):
            await event.answer("У вас нет прав на использование этого бота.")
            return
        return await handler(event, data)


async def get_next_duty():
    with open("list.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if datetime.now().weekday() in data["work_days"]:
        with open("list.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        duty = data["list"][data["queue"]]
        await bot.send_message(CHAT_ID, f"Дежурный на сегодня: {duty}")
        with open("list.json", "w", encoding="utf-8") as file:
            if data["queue"] >= len(data["list"]) - 1:
                data["queue"] = 0
            else:
                data["queue"] = data["queue"] + 1
            json.dump(data, file, ensure_ascii=False, indent=4)


async def disable_notifications():
    try:
        scheduler.remove_job("duty_notification")
        logging.info("Duty notification job removed")
    except Exception as e:
        logging.info(f"No active duty notification job to remove: {e}")

    with open("list.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data["enable"] = False
    with open("list.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def enable_notifications():
    # Remove existing job if it exists
    try:
        scheduler.remove_job("duty_notification")
        logging.info("Removed existing duty notification job")
    except Exception:
        logging.info("No existing duty notification job to remove")

    # Add new job
    scheduler.add_job(
        get_next_duty,
        "cron",
        day="*",
        hour=7,
        minute=45,
        id="duty_notification",
    )
    logging.info("Duty notification job scheduled for 7:45 AM")

    with open("list.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    data["enable"] = True
    with open("list.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Добро пожаловать в бот дежурств! Используйте /help для просмотра доступных команд."
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/help - Показать это сообщение помощи\n"
        "/ping - Проверить работу бота\n"
        "/next - Получить следующего дежурного\n"
        "/disable - Отключить уведомления\n"
        "/enable - Включить уведомления\n"
        "/status - Показать текущий статус"
    )
    await message.answer(help_text)


@dp.message(Command("ping"))
async def ping_command(message: Message):
    await message.answer("Понг!")


@dp.message(Command("status"))
async def status_command(message: Message):
    with open("list.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    work_days_str = ", ".join([weekdays[day] for day in data["work_days"]])

    current_duty = data["list"][data["queue"]] if data["list"] else "Не назначен"

    if data["enable"]:
        status_text = (
            f"✅ Уведомления включены\n"
            f"👥 Всего дежурных: {len(data["list"])}\n"
            f"📍 Текущая позиция: {data["queue"] + 1} ({current_duty})\n"
            f"📅 Рабочие дни: {work_days_str}"
        )
    else:
        status_text = (
            f"❌ Уведомления отключены\n"
            f"👥 Всего дежурных: {len(data["list"])}\n"
            f"📍 Текущая позиция: {data["queue"] + 1} ({current_duty})\n"
            f"📅 Рабочие дни: {work_days_str}"
        )

    await message.answer(status_text)


@dp.message(Command("enable"))
async def enable_notifications_command(message: Message):
    await enable_notifications()
    await message.answer("Уведомления включены.")


@dp.message(Command("disable"))
async def disable_notifications_command(message: Message):
    await disable_notifications()
    await message.answer("Уведомления отключены.")


@dp.message(Command("next"))
async def next_duty_command(message: Message):
    await get_next_duty()


async def main():
    dp.message.middleware(AdminMiddleware())

    # Start scheduler first
    scheduler.start()

    # Check if notifications should be enabled on startup
    with open("list.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if data["enable"]:
        await enable_notifications()

    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
    finally:
        await bot.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
