# bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from parse_expense import parse_expense
from db_handler import save_expense, update_last_field, get_today_purchases
from transcribe_with_denoise import transcribe_with_denoise

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message):
    await message.answer(
        "Привет! Я бот-оркестратор.\n\n"
        "• Добавить новую трату: просто напиши «категория подкатегория цена».\n"
        "• Исправить поле в последней записи:\n"
        "  – «Категория НовоеЗначение»\n"
        "  – «Подкатегория НовоеЗначение»\n"
        "  – «Цена НовоеЗначение»\n"
        "• Показать список сегодняшних трат: напиши «список»."
    )


async def handle_new_expense(raw: str, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or ""

    await message.answer("🔍 Отправляю в парсер…")
    category, subcategory, price = parse_expense(raw)

    if not (category and subcategory and price):
        return await message.answer("❌ Парсер не смог извлечь данные. Проверь формат.")

    await message.answer(
        f"🤖 Парсер вернул:\n"
        f"• Категория: <b>{category}</b>\n"
        f"• Подкатегория: <b>{subcategory}</b>\n"
        f"• Цена: <b>{price}</b>",
        parse_mode="HTML"
    )

    try:
        await save_expense(user_id, chat_id, username, category, subcategory, float(price))
        await message.answer("✅ Новая запись добавлена в БД.")
    except Exception as e:
        logging.exception("Ошибка сохранения в БД")
        await message.answer(f"❌ Не удалось сохранить: {e}")


async def handle_correction(field: str, new_val: str, message: Message):
    user_id = message.from_user.id
    await message.answer(f"✏️ Обновляю поле <b>{field}</b> на «{new_val}»…", parse_mode="HTML")
    try:
        ok = await update_last_field(user_id, field, new_val)
        if ok:
            await message.answer("✅ Поле обновлено.")
        else:
            await message.answer("⚠️ Нет предыдущей записи для обновления.")
    except ValueError as ve:
        await message.answer(f"❌ {ve}")
    except Exception as e:
        logging.exception("Ошибка обновления")
        await message.answer(f"❌ Не удалось обновить: {e}")


@dp.message(lambda m: m.text and not m.voice)
async def text_handler(message: Message):
    text = message.text.strip()
    lower = text.lower()

    # Список за сегодня
    if lower == "список":
        rows = await get_today_purchases(message.from_user.id)
        if not rows:
            return await message.answer("Сегодня ещё нет записей.")
        lines = [
            f"{r['ts'].strftime('%H:%M:%S')} — {r['category']} / {r['subcategory']} = {r['price']}"
            for r in rows
        ]
        return await message.answer("\n".join(lines))

    # Коррекция полей
    if lower.startswith("категория"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.answer("❌ Укажите значение после «Категория»")
        return await handle_correction("category", parts[1].strip(), message)

    if lower.startswith("подкатегория"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.answer("❌ Укажите значение после «Подкатегория»")
        return await handle_correction("subcategory", parts[1].strip(), message)

    if lower.startswith("цена"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            return await message.answer("❌ Укажите значение после «Цена»")
        return await handle_correction("price", parts[1].strip(), message)

    # Иначе — новая запись
    await handle_new_expense(text, message)


@dp.message(lambda m: m.voice)
async def voice_handler(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message.answer("🎙️ Начал распознавание аудио…")
    file = await bot.get_file(message.voice.file_id)
    local_path = f"voice_{message.voice.file_id}.ogg"
    await bot.download_file(file.file_path, destination=local_path)

    try:
        raw = transcribe_with_denoise(input_file=local_path, whisper_model="base", language="ru")
        await message.answer(f"🗣️ Распознал так: {raw}")
    except Exception as e:
        await message.answer(f"❌ Ошибка распознавания: {e}")
        os.remove(local_path)
        return
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

    # Обрабатываем распознанный текст как обычное сообщение
    # Используем ту же логику, что и в text_handler
    # Просто передаем raw-строку
    # Сначала проверяем "список" и коррекции, иначе новая запись
    lower = raw.lower().strip()
    if lower == "список":
        # импортируем здесь, чтобы избежать циклических зависимостей
        rows = await get_today_purchases(user_id)
        if not rows:
            return await message.answer("Сегодня ещё нет записей.")
        lines = [
            f"{r['ts'].strftime('%H:%M:%S')} — {r['category']} / {r['subcategory']} = {r['price']}"
            for r in rows
        ]
        return await message.answer("\n".join(lines))

    if lower.startswith("категория"):
        parts = raw.split(maxsplit=1)
        return await handle_correction("category", parts[1].strip() if len(parts)>1 else "", message)

    if lower.startswith("подкатегория"):
        parts = raw.split(maxsplit=1)
        return await handle_correction("subcategory", parts[1].strip() if len(parts)>1 else "", message)

    if lower.startswith("цена"):
        parts = raw.split(maxsplit=1)
        return await handle_correction("price", parts[1].strip() if len(parts)>1 else "", message)

    # Иначе — новая запись
    await handle_new_expense(raw, message)


async def main():
    logging.info("Запуск polling…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
