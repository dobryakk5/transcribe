# handlers_common.py
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import BufferedInputFile
from db_handler import update_last_field, get_today_purchases, get_user_purchases
from start_handlers import on_start
import pandas as pd
import textwrap
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

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

    # Формируем строки с подкатегорией и ценой (до 25 символов), цена с разделителями
    lines = [
        f"{r['subcategory'][:25]:<25} {int(r['price']):>10,}".replace(",", ".")
        for r in rows
    ]

    # Вычисляем общую сумму и добавляем итоговую строку
    total = sum(int(r['price']) for r in rows)
    lines.append("")
    lines.append(f"{'Итого сумма сегодня:':<25} {total:>10,}".replace(",", "."))

    await message.answer(f"<pre>{chr(10).join(lines)}</pre>", parse_mode="HTML")


# Pie chart display function
async def show_pie_chart(user_id: int, message: Message):
    rows = await get_user_purchases(user_id)
    if not rows:
        await message.answer("Нет данных для построения графика.")
        return

    category_totals = {}
    for row in rows:
        category = row["category"]
        price = float(row["price"])
        category_totals[category] = category_totals.get(category, 0) + price

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)

    await message.answer_photo(photo=BufferedInputFile(buffer.read(), filename="chart.png"))


# Bar chart by day function
async def show_bar_chart_by_day(user_id: int, message: Message):
    rows = await get_user_purchases(user_id)
    if not rows:
        await message.answer("Нет данных для построения графика.")
        return

    df = pd.DataFrame([dict(r) for r in rows])
    df["ts"] = pd.to_datetime(df["ts"])
    df["date"] = df["ts"].dt.date
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    grouped = df.groupby(["date", "category"])["price"].sum().unstack(fill_value=0)
    cumulative = grouped.cumsum()

    ax = cumulative.plot(kind="bar", stacked=True, figsize=(10, 6))
    ax.set_ylabel("Сумма")
    ax.set_xlabel("Дата")
    ax.set_xticklabels([d.strftime("%d.%m") for d in cumulative.index], rotation=0)
    ax.set_title("Кумулятивные оплаты по категориям")
    ax.legend(title="Категории", bbox_to_anchor=(1.05, 1), loc="upper left")

    fig = ax.get_figure()
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)

    await message.answer_photo(photo=BufferedInputFile(buffer.read(), filename="bar_chart.png"))

async def show_daily_bar_chart(user_id: int, message: Message):
    rows = await get_user_purchases(user_id)
    if not rows:
        await message.answer("Нет данных для построения графика.")
        return

    df = pd.DataFrame([dict(r) for r in rows])
    df["ts"] = pd.to_datetime(df["ts"])
    df["date"] = df["ts"].dt.date
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    grouped = df.groupby(["date", "category"])["price"].sum().unstack(fill_value=0)

    ax = grouped.plot(kind="bar", stacked=True, figsize=(10, 6))
    ax.set_ylabel("Сумма")
    ax.set_xlabel("Дата")
    ax.set_xticklabels([d.strftime("%d.%m") for d in grouped.index], rotation=0)
    ax.set_title("Ежедневные траты по категориям")
    ax.legend(title="Категории", bbox_to_anchor=(1.05, 1), loc="upper left")

    fig = ax.get_figure()
    fig.tight_layout()
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)

    await message.answer_photo(photo=BufferedInputFile(buffer.read(), filename="daily_bar_chart.png"))

async def export_purchases_to_excel(user_id: int, filename: str):
    rows = await get_user_purchases(user_id)

    data = []
    for row in rows:
        price_str = f"{int(row['price']):,}".replace(",", ".")
        data.append({
            'Категория': row['category'],
            'Подкатегория': row['subcategory'],
            'Цена': price_str,
            'Дата': row['ts'].astimezone(tz=None).replace(tzinfo=None).strftime("%d.%m.%Y %H:%M")
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
    time_col = header.index('Дата') + 1

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

    # Кнопка «Инструкция»
    if lower == "📘 инструкция":
        await message.answer(
        textwrap.dedent("""\
            💸 Добавить новую оплату: напиши «категория подкатегория цена».
            🧾 Загрузить позиции с чека: отправь фото QR-кода с чека
            🎙️ Загрузить простую транзакцию голосом: запиши голосовое.
            🛠️ Исправить поле в последней записи:
              – «Категория НовоеЗначение»
              – «Подкатегория НовоеЗначение»
              – «Цена НовоеЗначение»
            📋 Показать список сегодняшних оплат: меню «Список» 
            🔢 Выгрузить все оплаты в Excel: меню «Таблица» 
            💰 Добавить свои доходы: напиши "доход консультация 49505"
             - слово "доход" в начале говорит боту писать консультацию в доходы.

            Обновить бота 🔄: напиши /start 
        """)
        )
        return

    if lower == "📈 графики":
        await message.answer(
            "📊 Что показать?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔘 Круг по категориям")],
                    [KeyboardButton(text="📊 Накопительно категория/день")],
                    [KeyboardButton(text="📊 Ежедневно категория/день")],
                    [KeyboardButton(text="🏠 Главное меню")]
                ],
                resize_keyboard=True
            )
        )
        return

    if lower == "💰 доходы":
        from db_handler import get_user_incomes_days
        rows = await get_user_incomes_days(message.from_user.id, 30)
        if not rows:
            return await message.answer("Доходов за последние 30 дней нет.")
        lines = [
            f"{r['source'][:25]:<25} {int(r['amount']):>10,}".replace(",", ".")
            for r in rows
        ]
        total = sum(int(r['amount']) for r in rows)
        lines.append("")
        lines.append(f"{'Итого за 30 дней:':<25} {total:>10,}".replace(",", "."))
        await message.answer(f"<pre>{chr(10).join(lines)}</pre>", parse_mode="HTML")
        return

    if lower == "🔘 круг по категориям":
        await show_pie_chart(message.from_user.id, message)
        return

    if lower == "📊 накопительно категория/день":
        await show_bar_chart_by_day(message.from_user.id, message)
        return

    if lower == "📊 ежедневно категория/день":
        await show_daily_bar_chart(message.from_user.id, message)
        return

    if lower == "🏠 главное меню":
        await on_start(message)
        return

    if lower == "📄 список":
        await show_today_purchases(message.from_user.id, message)
        return

    if lower == "🔢 таблица":
        import os
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
