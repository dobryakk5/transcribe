import os
import math
import requests
from io import BytesIO
from aiogram.types import Message
from pyzbar.pyzbar import decode
from PIL import Image

from parse_expense import parse_expense_ph  # распределение категорий
from db_handler import save_expenses_ph   # функция сохранения списка в БД

FNS_TOKEN = os.getenv('FNS_TOKEN')


async def handle_photo_message(message: Message):
    """
    Обработчик фото: декодирует QR, проверяет чек на proverkacheka,
    распределяет категории, выводит позиции и сохраняет их в БД.
    """
    await message.answer("📷 Получил фото, распознаю QR-код…")

    # Скачать картинку в память
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    buffer = BytesIO()
    await message.bot.download_file(file.file_path, buffer)
    buffer.seek(0)

    # Открыть и декодировать QR
    try:
        img = Image.open(buffer)
    except Exception as e:
        return await message.answer(f"❌ Не удалось открыть изображение: {e}")

    decoded = decode(img)
    if not decoded:
        return await message.answer("❌ QR-код не найден на фото.")

    qr_raw = decoded[0].data.decode('utf-8')
    await message.answer(f"🔍 RAW QR: <code>{qr_raw}</code>", parse_mode="HTML")

    # Проверка чека на proverkacheka
    url = 'https://proverkacheka.com/api/v1/check/get'
    payload = {'token': FNS_TOKEN, 'qrraw': qr_raw}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return await message.answer(f"❌ Ошибка при проверке чека: {e}")

    result = resp.json()
    if result.get('code') != 1:
        return await message.answer(f"❌ API вернул ошибку: {result}")

    raw_items = result['data']['json'].get('items', [])
    if not raw_items:
        return await message.answer("⚠️ В ответе нет позиций товаров.")

    # Составляем список кортежей (название, сумма_в_копейках)
    items_with_price = [
        (it.get('name', '').strip(), it.get('sum', 0))
        for it in raw_items
    ]

    # Получаем категории
    categorized = parse_expense_ph(items_with_price)

    # 1) Выводим в чат
    lines = ["📋 Позиции чека с категориями:"]
    for cat, name, sum_kopek in categorized:
        rub = math.ceil(sum_kopek / 100)
        cat_disp = cat or "(не определено)"
        lines.append(f"• {cat_disp} — {name} — {rub} ₽")
    await message.answer("\n".join(lines))

    # 2) Готовим список для сохранения: (category, name, price_float)
    items_to_save = []
    for cat, name, sum_kopek in categorized:
        if not (cat and name and isinstance(sum_kopek, (int, float))):
            continue
        price_rub = math.ceil(sum_kopek / 100)
        items_to_save.append((cat, name, float(price_rub)))

    # 3) Сохраняем в БД
    if items_to_save:
        try:
            await save_expenses_ph(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                username=message.from_user.username or "",
                items=items_to_save
            )
            await message.answer(f"✅ Сохранено в БД: {len(items_to_save)} позиций.")
        except Exception as e:
            await message.answer(f"❌ Ошибка при сохранении в БД: {e}")
    else:
        await message.answer("⚠️ Нет корректных позиций для сохранения.")
