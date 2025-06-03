from datetime import datetime
import pytz

# moscow_tz = pytz.timezone("Europe/Moscow")
#now_with_tz = datetime.now(pytz.timezone("Europe/Moscow"))  # С временной зоной
#naive_time = now_with_tz.replace(tzinfo=None, microsecond=0)


naive_time = datetime.now(pytz.timezone("Europe/Moscow")).replace(tzinfo=None, microsecond=0)

print(naive_time)  # Пример: 2024-06-20 15:30:00 (без временной зоны)