import plotly.express as px
import plotly.io as pio
from telegram import Bot

# Создание графика
fig = px.line(x=[1, 2, 3], y=[4, 1, 2], title="Пример графика")

# Сохранение графика в файл
pio.write_image(fig, 'plot.png')

# Отправка изображения через Telegram-бота
bot = Bot(token='API_TOKEN')
bot.send_photo(chat_id='CHAT_ID', photo=open('plot.png', 'rb'))
