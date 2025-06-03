# handlers_common.py
from aiogram.types import Message
from db_handler import update_last_field, get_today_purchases


async def show_parser_result(category: str, subcategory: str, price: str, message: Message):
    """Показывает результат работы парсера"""
    await message.answer(
        f"🤖 Парсер вернул:\n"
        f"• Категория: <b>{category}</b>\n"
        f"• Подкатегория: <b>{subcategory}</b>\n"
        f"• Цена: <b>{price}</b>",
        parse_mode="HTML"
    )


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
        await message.answer(f"❌ Не удалось обновить: {e}")


async def show_today_purchases(user_id: int, message: Message):
    rows = await get_today_purchases(user_id)
    if not rows:
        return await message.answer("Сегодня ещё нет записей.")
    
    lines = [
        f"{r['ts'].strftime('%H:%M:%S')} — {r['category']} / {r['subcategory']} = {r['price']}"
        for r in rows
    ]
    await message.answer("\n".join(lines))


async def process_user_input(
    raw_text: str, 
    message: Message,
    handle_new_expense_func
):
    """Общий обработчик ввода с гибкой передачей функции обработки новой записи"""
    lower = raw_text.lower().strip()

    if lower == "список":
        await show_today_purchases(message.from_user.id, message)
        return

    correction_commands = {
        "категория": "category",
        "подкатегория": "subcategory",
        "цена": "price"
    }
    
    for prefix, field in correction_commands.items():
        if lower.startswith(prefix):
            parts = raw_text.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                return await message.answer(f"❌ Укажите значение после «{prefix.capitalize()}»")
            return await handle_correction(field, parts[1].strip(), message)

    await handle_new_expense_func(raw_text, message)