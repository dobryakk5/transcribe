import os
import math
import requests
from io import BytesIO
from aiogram.types import Message
from pyzbar.pyzbar import decode
from PIL import Image
from parse_expense_ph import parse_expense_ph  # импорт функции распределения категорий

# FNS_TOKEN подгружается из переменных окружения (из main.py через load_dotenv)
FNS_TOKEN = os.getenv('FNS_TOKEN')

async def handle_photo_message(message: Message):
    """
    Обработчик фотографий: декодирует QR-код из фото, проверяет чек на proverkacheka.com,
    распределяет категории и выводит позиции тßоваров.
    """
    await message.answer("📷 Получил фото, распознаю QR-код…")

    # Скачиваем в память через Bot API
    photo = message.photo[-1]
    # Получаем путь к файлу
    file = await message.bot.get_file(photo.file_id)
    buffer = BytesIO()
    # Загружаем содержимое в BytesIO
    await message.bot.download_file(file.file_path, buffer)
    buffer.seek(0)

    # Открываем изображение из BytesIO
    try:
        img = Image.open(buffer)
    except Exception as e:
        return await message.answer(f"❌ Не удалось открыть изображение: {e}")

    # Декодируем первый QR-код
    decoded = decode(img)
    if not decoded:
        return await message.answer("❌ QR-код не найден на фото.")

    qr_raw = decoded[0].data.decode('utf-8')
    await message.answer(f"🔍 RAW QR: <code>{qr_raw}</code>", parse_mode="HTML")

    # Проверяем чек
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

    items = result['data']['json'].get('items', [])
    if not items:
        return await message.answer("⚠️ В ответе нет позиций товаров.")

    # Составляем список (name, price) из ответа
    raw_items = [(it.get('name', '').strip(), it.get('sum', 0)) for it in items]

    # Получаем категории для каждого товара
    categorized = parse_expense_ph(raw_items)

    # Формируем вывод: категория — товар — рубли (округл. вверх)
    lines = ["📋 Позиции чека с категориями:"]
    for cat, name, sum_kopek in categorized:
        rub = math.ceil(sum_kopek / 100)
        cat_display = cat or "(не определено)"
        lines.append(f"• {cat_display} — {name} — {rub} ₽")

    await message.answer("\n".join(lines))
