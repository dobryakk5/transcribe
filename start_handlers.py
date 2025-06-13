import textwrap
import os
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from itsdangerous import URLSafeSerializer

# Загружаем секрет из окружения
API_TOKEN = os.getenv("FNS_TOKEN")
serializer = URLSafeSerializer(API_TOKEN, salt="uid-salt")

from urllib.parse import quote

async def on_start(message: Message):

    # Подписываем Telegram user_id
    uid = message.from_user.id
    token = serializer.dumps(uid)
    # Ссылка на внешний сайт с токеном
    url = f"https://ai5.space/?auth={quote(token)}"

    # 1) Reply-клавиатура для команд
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Инструкция")],
            [KeyboardButton(text="📄 Список"), KeyboardButton(text="🔢 Таблица")],
            [KeyboardButton(text="📈 Графики")],
            [KeyboardButton(text="💰 Доходы")]
        ],
        resize_keyboard=True
    )

    # Отправляем основное меню
    await message.answer("🚪 Привет!",
        reply_markup=reply_kb
    )

    # 2) Inline-клавиатура для перехода в веб-кабинет
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Переход в личный кабинет", url=url)]
        ]
    )

    await message.answer(
        textwrap.dedent("""\
         Я финансовый аналитик 🤖
            
            Максимально просто сохраняю покупки в Вашу базу данных (БД).
            
            Просто скажите: "мороженое 200 рублей" или "книга тыщапятьсот"
                        
            Используйте текст, голосовые сообщения и чеки для добавления в БД.
            Я всё распознаю с помощью ИИ.
                                    
            📌 Меню:
            • Инструкция — справка по командам
            • Список — сегодняшние оплаты
            • Таблица — выгрузка всех оплат в Excel
            • Графики — визуализация данных
            • Кабинет — редактирование всего
        """),
        reply_markup=reply_kb
    )
    await message.answer("🚪 Открыть кабинет в браузере",reply_markup=inline_kb)
