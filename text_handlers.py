# text_handlers.py
from aiogram.types import Message
from handlers_common import process_user_input, show_parser_result
from parse_expense import parse_expense_t
from db_handler import save_expense

from db_handler import save_income

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


# ----------- ДОХОДЫ -----------
async def handle_new_income_t(raw: str, message: Message):
    """Обработка новой записи дохода"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username or ""

    try:
        source, amount_str = raw.rsplit(maxsplit=1)
        amount = float(amount_str)
    except Exception:
        return await message.answer("❌ Неверный формат. Пример: доход личное 12500")

    await message.answer(f"💰 Источник: {source}, Сумма: {int(amount):,}".replace(",", "."))

    try:
        await save_income(user_id, source, amount)
        await message.answer("✅ Доход успешно добавлен в БД.")
    except Exception as e:
        await message.answer(f"❌ Не удалось сохранить доход: {e}")


async def handle_text_message(message: Message):
    text = message.text.strip()
    command, *rest = text.split(maxsplit=1)

    if command.lower() == "доход" and rest:
        raw_income = rest[0]
        await handle_new_income_t(raw_income, message)
    else:
        await process_user_input(
            raw_text=text,
            message=message,
            handle_new_expense_func=handle_new_expense_t
        )