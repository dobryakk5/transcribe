# main.py
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramForbiddenError
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
    try:
        await on_start(message)
    except TelegramForbiddenError:
        logging.warning(f"Пользователь {message.from_user.id} заблокировал бота")
        # Здесь можно добавить логику обновления БД
    except Exception as e:
        logging.error(f"Ошибка в обработчике старта: {e}")

# Регистрация обработчиков с обработкой ошибок
async def safe_text_handler(message):
    try:
        await handle_text_message(message)
    except TelegramForbiddenError:
        logging.warning(f"Пользователь {message.from_user.id} заблокировал бота")
        # Обновить статус пользователя в БД
    except Exception as e:
        logging.error(f"Ошибка обработки текста: {e}")

async def safe_voice_handler(message):
    try:
        await handle_voice_message(message)
    except TelegramForbiddenError:
        logging.warning(f"Пользователь {message.from_user.id} заблокировал бота")
    except Exception as e:
        logging.error(f"Ошибка обработки голоса: {e}")

async def safe_photo_handler(message):
    try:
        await handle_photo_message(message)
    except TelegramForbiddenError:
        logging.warning(f"Пользователь {message.from_user.id} заблокировал бота")
    except Exception as e:
        logging.error(f"Ошибка обработки фото: {e}")

dp.message.register(safe_text_handler, F.text & ~F.voice & ~F.photo)
dp.message.register(safe_voice_handler, F.voice)
dp.message.register(safe_photo_handler, F.photo)

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
    try:
        await dp.start_polling(bot)
    except TelegramForbiddenError as e:
        logging.error(f"Бот заблокирован пользователем: {e}")
    except Exception as e:
        logging.exception("Критическая ошибка в polling")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.exception("Непредвиденная ошибка")