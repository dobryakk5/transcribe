#main.py
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

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message):
    await on_start(message)

# Регистрация обработчиков
dp.message.register(handle_text_message, F.text & ~F.voice & ~F.photo)
dp.message.register(handle_voice_message, F.voice)
dp.message.register(handle_photo_message, F.photo)


from logging.handlers import TimedRotatingFileHandler

# Убедиться, что папка logs существует
os.makedirs("logs", exist_ok=True)

# Создаём логгер
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Хендлер для файла в папке logs
file_handler = TimedRotatingFileHandler(
    "logs/bot.log",       # путь к лог-файлу
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

# Хендлер для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем хендлеры к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)


async def main():
    logging.info("Запуск polling…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
