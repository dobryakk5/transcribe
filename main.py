# main.py
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from text_handlers import handle_text_message
from voice_handlers import handle_voice_message

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        "Привет! Я бот-аналитик.\n\n"
        "• Добавить новую трату: просто напиши «категория подкатегория цена».\n"
        "• Исправить поле в последней записи:\n"
        "  – «Категория НовоеЗначение»\n"
        "  – «Подкатегория НовоеЗначение»\n"
        "  – «Цена НовоеЗначение»\n"
        "• Показать список сегодняшних трат: напиши «список»."
    )


# Регистрация обработчиков
dp.message.register(handle_text_message, F.text & ~F.voice)
dp.message.register(handle_voice_message, F.voice)


async def main():
    logging.info("Запуск polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")