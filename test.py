измени этот старый скрипт и внедри туда новый функционал

import uuid
import redis
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import textwrap
import os
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# Загружаем секрет из окружения
API_TOKEN = os.getenv("API_TOKEN")



# Настройки Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Инициализация бота
BOT_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Создаём Inline-клавиатуру с одной кнопкой
menu_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Получить ссылку для входа", callback_data="get_dash_url"))

@dp.callback_query_handler(lambda c: c.data == 'get_dash_url')
async def process_get_url(callback_query: types.CallbackQuery):
    """
    Обработка нажатия на кнопку:
    - Генерация токена
    - Сохранение в Redis с TTL 5 минут
    - Отправка пользователю ссылки
    """
    user_id = callback_query.from_user.id
    # Генерируем уникальный токен
    token = str(uuid.uuid4())
    # Сохраняем токен в Redis: dash_token:<token> → user_id (TTL=300 секунд)
    r.setex(f"dash_token:{token}", 300, user_id)
    # Формируем ссылку
    dash_url = f"https://ai5.space/auth?token={token}"
    # Отвечаем на callback, убираем «часики» у кнопки
    await bot.answer_callback_query(callback_query.id)
    # Отправляем саму ссылку
    await bot.send_message(
        chat_id=user_id,
        text=f"Ваша ссылка для входа (действительна 5 минут):\n{dash_url}"
    )

if __name__ == '__main__':
    # Опционально: регистрируем команду в меню бота
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="/start", description="Запустить бота и получить меню")
    ]
    asyncio.get_event_loop().run_until_complete(bot.set_my_commands(commands))

    # Запуск поллинга
    executor.start_polling(dp, skip_updates=True)




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

старую попытку внедрить меню "кабинет" убери
Кабинет будет последним в общем меню

