import openai
import os
import re
from dotenv import load_dotenv

# Настройки OpenRouter
load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_BASE = 'https://openrouter.ai/api/v1'
LLM_MODEL = 'deepseek/deepseek-chat-v3-0324:free'

def parse_expense(raw_input: str) -> tuple:
    """
    Извлекает структурированные данные из сырой строки с возможными ошибками
    Возвращает кортеж: (категория, подкатегория, цена)
    
    Параметры:
        raw_input (str): Сырая строка формата "категория подкатегория цена"
    
    Возвращает:
        tuple: (категория, подкатегория, цена) или (None, None, None) при ошибке
    """
    # Формируем промпт с инструкциями и примерами
    prompt = f"""<｜begin▁of▁task｜>
Извлеки из текста три элемента: категорию, подкатегорию (товар/услуга) и цену. 
Исправь опечатки, приведи слова к нормальной форме. Цену выведи цифрами.
Если не определил категорию или подкатегорию, то найди созвучное слово для категории товара/услуги или подкатегории - самого товара/услуги.
Если нашлась категория, то можешь понять по смыслу и созвучию подкатегорию и наоборот, но только если слово непонятно.
Правильные слова не подменяй.
Если нет цифры с ценой, то не выдумывай и не пиши цену.

Формат вывода СТРОГО: категория|подкатегория|цена

Примеры:
1. Ввод: "еда ведро картошки 500 рублей" → еда|картошка|500
2. Ввод: "транспорт такси до аэропорта 1500 руб" → транспорт|такси|1500
3. Ввод: "развлечния кинотеатр 300 рубли" → развлечения|кинотеатр|300
4. Ввод: "быт хоз мыло 75 р" → быт|мыло|75
5. Ввод: "эдл малако 80" → еда|молоко|80

Обработай:
Ввод: "{raw_input}"
<｜end▁of▁task｜>
Вывод:"""

    try:
        # Отправка запроса к ИИ
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_base=OPENROUTER_API_BASE,
            headers={
                "HTTP-Referer": "https://localhost",  # Замените на реальные данные
                "X-Title": "Counter"
            },
            api_key=OPENROUTER_API_KEY,
            max_tokens=50,
            temperature=0.1
        )
        
        # Извлекаем ответ
        ai_output = response['choices'][0]['message']['content'].strip()
        
        # Парсим результат
        if "|" in ai_output:
            parts = ai_output.split("|")
            if len(parts) >= 3:
                # Извлекаем только цифры из цены (на случай если ИИ добавил текст)
                price_value = re.search(r'\d+', parts[2])
                price = price_value.group() if price_value else None
                
                return (
                    parts[0].strip().lower(),
                    parts[1].strip().lower(),
                    price
                )
        
        # Если формат не совпадает - вернуть ошибку
        print(f"Неверный формат ответа ИИ: {ai_output}")
        return None, None, None
        
    except Exception as e:
        print(f"Ошибка при обработке: {str(e)}")
        return None, None, None