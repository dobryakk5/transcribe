import asyncio
import logging
import os
import textwrap

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from text_handlers import handle_text_message
from voice_handlers import handle_voice_message
from photo_handlers import handle_photo_message

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def on_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Инструкция")],
            [KeyboardButton(text="Список")],
            [KeyboardButton(text="Таблица")],
        ],
        resize_keyboard=True
    )
    await message.answer(
        textwrap.dedent("""\
            Привет! Я финансовый помощник 🤖
            
            Максимально просто сохраняю покупки в вашу базу данных(БД).
            Используйте текст, голосовые сообщения и чеки для добавления в БД.
            Я все распознаю с поощью ИИ.
                                    
            Какие сейчас настроены кнопки:
            • Инструкция — вывести справку по командам
            • Список — показать сегодняшние оплаты текстом
            • Таблица — выгрузить все оплаты в Excel
        """),
        reply_markup=keyboard
    )

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
