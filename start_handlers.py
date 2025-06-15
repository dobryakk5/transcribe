from aiogram.types import Message

import textwrap
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
)

async def on_start(message: Message):

    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Инструкция")],
            [KeyboardButton(text="📄 Список"), KeyboardButton(text="🔢 Таблица")],
            [KeyboardButton(text="📈 Графики")],
            [KeyboardButton(text="💰 Доходы")],
            [KeyboardButton(text="🚪 Кабинет")]

        ],
        resize_keyboard=True
    )

    # Отправляем основное меню
    await message.answer(" Привет, {message.from_user.first_name}!",
        reply_markup=reply_kb
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
