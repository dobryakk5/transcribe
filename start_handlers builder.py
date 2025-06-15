import textwrap
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from itsdangerous import URLSafeSerializer
import os

# создаём сериализатор один раз
API_TOKEN = os.getenv("API_TOKEN")
serializer = URLSafeSerializer(API_TOKEN, salt="uid-salt")

async def on_start(message: Message):
    # Подписываем user_id в токен
    uid = message.from_user.id
    token = serializer.dumps(uid)
    url = f"https://ai5.space/?token={token}"

        # Объединённое меню через ReplyKeyboardBuilder
    builder = ReplyKeyboardBuilder()
    # Кнопки меню
    builder.button(text="📘 Инструкция")
    builder.button(text="📄 Список")
    builder.button(text="🔢 Таблица")
    builder.button(text="📈 Графики")
    builder.button(text="💰 Доходы")
    # Кнопка для перехода на веб-сайт кабинета
    builder.button(text="🚪 Кабинет", web_app=WebAppInfo(url=url))
    # Расположение кнопок: 1, 2, 1, 1, 1
    builder.adjust(1, 2, 1, 1, 1)
    markup = builder.as_markup(resize_keyboard=True)

    # Отправляем сообщение с меню и описанием    
    await message.answer(
        textwrap.dedent("""\
            Привет! Я финансовый помощник 🤖
            
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
        reply_markup=markup
    )