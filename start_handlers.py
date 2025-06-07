from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import textwrap

async def on_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Инструкция")],
            [KeyboardButton(text="📄 Список")],
            [KeyboardButton(text="🔢 Таблица")],
            [KeyboardButton(text="📈 Графики")],
        ],
        resize_keyboard=True
    )
    await message.answer(
        textwrap.dedent("""\
            Привет! Я финансовый помощник 🤖
            
            Максимально просто сохраняю покупки в вашу базу данных (БД).
                        
            Используйте текст, голосовые сообщения и чеки для добавления в БД.
            Я всё распознаю с помощью ИИ.
                                    
            📌 Меню:
            • Инструкция — справка по командам
            • Список — сегодняшние оплаты
            • Таблица — выгрузка всех оплат в Excel
            • Графики — визуализация данных
        """),
        reply_markup=keyboard
    )