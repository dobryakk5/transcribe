import easyocr
import re

def parse_receipt(image_path):
    reader = easyocr.Reader(['ru', 'en'])  # Поддержка русского и английского языков
    results = reader.readtext(image_path, detail=0)

    items = []
    total = None

    # Регулярное выражение для поиска цен (например, 123.45 или 123,45)
    price_pattern = re.compile(r'(\d+[.,]\d{2})')

    for line in results:
        # Поиск строки с итоговой суммой
        if re.search(r'итого|итог|total', line, re.IGNORECASE):
            match = price_pattern.search(line)
            if match:
                total = match.group(1).replace(',', '.')
            continue

        # Поиск строк с товарами и ценами
        matches = price_pattern.findall(line)
        if matches:
            price = matches[-1].replace(',', '.')
            # Удаление цены из строки, чтобы получить название товара
            item_name = price_pattern.sub('', line).strip(' .:-')
            items.append((item_name, price))

    return items, total
