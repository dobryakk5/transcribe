from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
import asyncio
import logging
import os
from dotenv import load_dotenv

from text_handlers import handle_text_message
from voice_handlers import handle_voice_message
from photo_handlers import handle_photo_message
from start_handlers import on_start

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message):
    await on_start(message)

# Регистрация обработчиков
dp.message.register(handle_text_message, F.text & ~F.voice & ~F.photo)
dp.message.register(handle_voice_message, F.voice)
dp.message.register(handle_photo_message, F.photo)

async def main():
    logging.info("Запуск polling…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
