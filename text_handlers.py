# text_handlers.py
from aiogram.types import Message
from handlers_common import process_user_input, show_parser_result
from parse_expense import parse_expense_t
from db_handler import save_expense

async def handle_new_expense_t(raw: str, message: Message):
    """Обработка новой записи для текстовых сообщений"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or ""

    category, subcategory, price = parse_expense_t(raw)

    if not (category and subcategory and price):
        return await message.answer("❌ Парсер не смог извлечь данные. Проверь формат.")

    # Показываем результат парсера
    await show_parser_result(category, subcategory, price, message)

    try:
        await save_expense(user_id, chat_id, username, category, subcategory, float(price))
        await message.answer("✅ Новая запись добавлена в БД.")
    except Exception as e:
        await message.answer(f"❌ Не удалось сохранить: {e}")


async def handle_text_message(message: Message):
    text = message.text.strip()
    await process_user_input(
        raw_text=text,
        message=message,
        handle_new_expense_func=handle_new_expense_t
    )