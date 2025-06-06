# handlers_common.py
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile
from db_handler import update_last_field, get_today_purchases, get_user_purchases
import pandas as pd


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
    field_names = {
        'category': 'Категория',
        'subcategory': 'Подкатегория',
        'price': 'Цена'
    }
    field_rus = field_names.get(field, field)
    await message.answer(f"✏️ Обновляю поле <b>{field_rus}</b> на «{new_val}»…", parse_mode="HTML")
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


async def export_purchases_to_excel(user_id: int, filename: str):
    rows = await get_user_purchases(user_id)

    data = []
    for row in rows:
        price_str = f"{int(row['price']):,}".replace(",", ".")
        time_str = row['ts'].astimezone(tz=None).replace(tzinfo=None).strftime("%d.%m.%Y")
        data.append({
            'Категория': row['category'],
            'Подкатегория': row['subcategory'],
            'Цена': price_str,
            'Время': time_str
        })

    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

    # Форматирование Excel
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment

    wb = load_workbook(filename)
    ws = wb.active

    for col in ws.columns:
        max_len = max((len(str(c.value)) for c in col if c.value), default=0)
        ws.column_dimensions[col[0].column_letter].width = max_len + 2

    header = [cell.value for cell in ws[1]]
    price_col = header.index('Цена') + 1
    time_col = header.index('Время') + 1

    for row in ws.iter_rows(min_row=2, min_col=price_col, max_col=price_col):
        row[0].alignment = Alignment(horizontal='right')

    for row in ws.iter_rows(min_row=2, min_col=time_col, max_col=time_col):
        row[0].alignment = Alignment(horizontal='right')

    wb.save(filename)

async def process_user_input(
    raw_text: str, 
    message: Message,
    handle_new_expense_func
):
    lower = raw_text.lower().strip()

    if lower == "список":
        await show_today_purchases(message.from_user.id, message)
        return

    if lower == "таблица":
        import os
        from io import BytesIO
        filename = "Fin_a_bot.xlsx"
        await export_purchases_to_excel(message.from_user.id, filename)
        with open(filename, 'rb') as f:
            file_data = f.read()
        await message.answer_document(BufferedInputFile(file_data, filename))
        os.remove(filename)
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