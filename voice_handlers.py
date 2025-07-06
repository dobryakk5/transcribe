# voice_handlers.py
import os
import asyncio
from aiogram import Bot
from aiogram.types import Message
from transcribe_v import transcribe_v
from handlers_common import process_user_input, show_parser_result
from parse_expense import parse_expense_v
from db_handler import save_expense

async def show_processing_animation(chat_id: int, bot: Bot):
    """Анимация с постепенным добавлением точек"""
    base_text = "⏳ Распознаю голос"
    message = await bot.send_message(chat_id, base_text)
    
    # Создаем асинхронную задачу для анимации
    animation_task = asyncio.create_task(animate_dots(message, base_text))
    
    return message, animation_task

async def animate_dots(message: Message, base_text: str):
    """Обновляет сообщение, добавляя точки каждую секунду"""
    try:
        for i in range(1, 10):  # Максимум 9 точек
            dots = "." * i
            await message.edit_text(f"{base_text}{dots}")
            await asyncio.sleep(1)
    except Exception as e:
        # Игнорируем ошибки редактирования (например, если сообщение удалено)
        pass

async def handle_new_expense_v(raw: str, message: Message):
    """Обработка новой записи для голосовых сообщений"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or ""

    category, subcategory, price = parse_expense_v(raw)

    if not (category and subcategory and price):
        return await message.answer("❌ Парсер не смог извлечь данные.")

    await show_parser_result(category, subcategory, price, message)

    try:
        await save_expense(user_id, chat_id, username, category, subcategory, float(price))
        await message.answer("✅ Новая запись добавлена в БД.")
    except Exception as e:
        await message.answer(f"❌ Не удалось сохранить: {e}")

async def handle_voice_message(message: Message):
    bot = message.bot 
    # Показываем анимированный индикатор обработки
    status_msg, animation_task = await show_processing_animation(message.chat.id, bot)
    
    file = await bot.get_file(message.voice.file_id)
    local_path = f"voice_{message.voice.file_id}.ogg"
    
    try:
        # Скачиваем файл
        await bot.download_file(file.file_path, destination=local_path)
        
        # Транскрибация
        raw = transcribe_v(input_file=local_path, 
                                    whisper_model="small", 
                                    language="ru")
        
        # Останавливаем анимацию и удаляем индикатор
        animation_task.cancel()
        await status_msg.delete()
        
        # Обработка результата
        await process_user_input(
            raw_text=raw,
            message=message,
            handle_new_expense_func=handle_new_expense_v
        )
        
    except Exception as e:
        # Останавливаем анимацию и удаляем индикатор в случае ошибки
        if 'animation_task' in locals():
            animation_task.cancel()
        if 'status_msg' in locals():
            await status_msg.delete()
        await message.answer(f"❌ Ошибка распознавания: {e}")
        
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)