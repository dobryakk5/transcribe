from pyzbar.pyzbar import decode
from PIL import Image
from urllib.parse import parse_qs, urlparse
import sys

def parse_qr_data(data):
    """
    Извлекает параметры из строки QR-кода.
    """
    parsed_url = urlparse(data)
    params = parse_qs(parsed_url.query)
    return {k: v[0] for k, v in params.items()}

def main(image_path):
    """
    Основная функция для декодирования QR-кода и извлечения данных.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"❌ Ошибка при открытии изображения: {e}")
        return

    decoded_objects = decode(img)
    if not decoded_objects:
        print("❌ QR-код не найден.")
        return

    for obj in decoded_objects:
        qr_data = obj.data.decode('utf-8')
        print(f"📦 Данные QR-кода: {qr_data}")
        receipt_info = parse_qr_data(qr_data)
        print("\n📄 Извлечённые данные:")
        for key, value in receipt_info.items():
            print(f"{key.upper()}: {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python qr.py путь_к_изображению")
    else:
        main(sys.argv[1])
