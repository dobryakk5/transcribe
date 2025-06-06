import openai
import os
import re
from dotenv import load_dotenv

# Настройки OpenRouter
load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_BASE = 'https://openrouter.ai/api/v1'
LLM_MODEL = 'deepseek/deepseek-chat-v3-0324:free'

def parse_expense_t(raw_input: str) -> tuple:
    """
    Извлекает структурированные данные из текстового ввода
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
Если было 3 слова и ты не знаешь что исправлять, то оставь как есть.
Правильные слова не подменяй, но знаки убирай из слов.
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
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://ai5.space",  # Замените на реальные данные
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


def parse_expense_ph(items_with_price):
    """
    Принимает список товаров с ценами и возвращает список кортежей:
    (категория, название_товара, цена)

    Параметры:
        items_with_price (list of tuples): [(name, price), ...]

    Возвращает:
        list of tuples: [(category, name, price), ...]
    """
    names = [name for name, price in items_with_price]

    prompt = """
У тебя есть список покупок с названиями товаров. Для каждого названия нужно определить категорию товара.
Категория должна быть одним словом (например: еда, быт, развлечения, ремонт и так далее).
Если категория товара не была определена, то определи её как none.
Возвращай список товаров в формате:
название1|категория1
название2|категория2
...

Список товаров:
"""
    for name in names:
        prompt += f"- {name}\n"
    prompt += "\nДай ответ строго в указанном формате без лишних пояснений."

    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            api_base=OPENROUTER_API_BASE,
            api_key=OPENROUTER_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=len(names) * 20
        )
        ai_output = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Ошибка при получении категорий товаров: {e}")
        return [(None, name, price) for name, price in items_with_price]

    # Разбираем вывод
    mapping = {}
    for line in ai_output.splitlines():
        if '|' in line:
            name, cat = line.split('|', 1)
            mapping[name.strip()] = cat.strip().lower() or None

    # Создаём исходный список с возможными None
    result = [(mapping.get(name, None), name, price) for name, price in items_with_price]

    # Проходим и заполняем None от соседей
    for i in range(len(result)):
        category, name, price = result[i]
        if not category or category in {"-", "неизвестно", "none"}:
            # Ищем вперёд
            for j in range(i + 1, len(result)):
                if result[j][0]:
                    result[i] = (result[j][0], name, price)
                    break
            else:
                # Ищем назад, если вперёд не нашли
                for j in range(i - 1, -1, -1):
                    if result[j][0]:
                        result[i] = (result[j][0], name, price)
                        break

    return result



def parse_expense_v(raw_input: str) -> tuple:
    """
    Извлекает структурированные данные из голосового ввода
    Возвращает кортеж: (категория, подкатегория, цена)
    
    Параметры:
        raw_input (str): Распознанный текст из аудио
    
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
Если есть только два значения: слово и цифра, значит это подкатегория и цена. Категорию придумай сам.

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
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://ai5.space",  # Замените на реальные данные
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