# main.py
import asyncio
import logging
import os
import textwrap

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from text_handlers import handle_text_message
from voice_handlers import handle_voice_message
from photo_handlers import handle_photo_message


load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        textwrap.dedent("""\
            Привет! Я бот-аналитик 🤖

            💸 Добавить новую оплату: просто напиши «категория подкатегория цена».
            🧾 Загрузить позиции с чека: отправь фото QR-кода с чека
            🎙️ Загрузить простую транзакцию голосом: запиши голосовое.
            🛠️ Исправить поле в последней записи:
              – «Категория НовоеЗначение»
              – «Подкатегория НовоеЗначение»
              – «Цена НовоеЗначение»
            📋 Показать список сегодняшних оплат: напиши «список».
            📈 Выгрузить все оплаты в Excel: напиши «таблица».
        """)
    )


# Регистрация обработчиков
dp.message.register(handle_text_message, F.text & ~F.voice)
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