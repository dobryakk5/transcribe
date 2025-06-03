# parse_receipt_tesseract.py

import re
import cv2
from PIL import Image
import pytesseract

# Если Tesseract не в PATH, раскомментируйте и укажите свой путь:
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Конфигурация для кириллицы + цифры + разделители
CUSTOM_CONFIG = (
    r'--oem 1 --psm 6 '
    r'-c tessedit_char_whitelist='
    r'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    r'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    r'0123456789.,'
)

PRICE_PATTERN = re.compile(r'(\d+[.,]\d{2})')
TOTAL_PATTERN = re.compile(r'(итого?|total)', re.IGNORECASE)


def preprocess_image(path: str) -> Image.Image:
    """
    Предобработка: серый, контраст, адаптивная бинаризация, морфологическое закрытие.
    Возвращает PIL Image.
    """
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Файл не найден: {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Контраст
    gray = cv2.equalizeHist(gray)
    # Увеличение размера для лучшего OCR
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    # Адаптивная бинаризация
    bin_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, blockSize=15, C=8
    )
    # Морфологическое закрытие
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    clean = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
    # Инвертируем, чтобы текст — чёрный на белом
    inv = cv2.bitwise_not(clean)
    return Image.fromarray(inv)


def fix_ocr_typos(s: str) -> str:
    """
    Простая пост-обработка: заменяем похожие символы.
    """
    mapping = {'0': 'О', '1': 'I', '5': 'S', '6': 'б', '8': 'В', 'l': 'т'}
    for k, v in mapping.items():
        s = s.replace(k, v)
    return s


def parse_receipt(path: str, debug: bool = False):
    """
    Возвращает:
      items: [(название, цена), ...]
      total: строка с общей суммой или None
    Если debug=True, возвращает ещё и raw_text.
    """
    img = preprocess_image(path)
    raw = pytesseract.image_to_string(img, lang='rus', config=CUSTOM_CONFIG)
    raw = fix_ocr_typos(raw)
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    items = []
    total = None
    for line in lines:
        # Итоговая строка
        if TOTAL_PATTERN.search(line):
            m = PRICE_PATTERN.search(line)
            if m:
                total = m.group(1).replace(',', '.')
            continue
        # Позиции товаров
        prices = PRICE_PATTERN.findall(line)
        if prices:
            price = prices[-1].replace(',', '.')
            name = PRICE_PATTERN.sub('', line).strip(' .:-')
            items.append((name, price))

    if debug:
        return items, total, raw
    return items, total


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Использование: python parse_receipt_tesseract.py путь_к_изображению")
        sys.exit(1)
    path = sys.argv[1]
    items, total, raw = parse_receipt(path, debug=True)
    print("=== DEBUG OCR OUTPUT ===")
    print(raw)
    print("\n=== PARSED ITEMS ===")
    for n, p in items:
        print(f"{n} — {p}")
    print(f"\nИтого: {total or 'не найдено'}")
