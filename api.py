from flask import Flask, request, jsonify
import os
import ffmpeg
import transcribe_with_denoise
import tempfile
import logging

# Инициализация Flask-приложения
app = Flask(__name__)
app.json.ensure_ascii = False  # Отключение ASCII-экранирования для корректного отображения русских символов

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к модели RNNoise
RNNOISE_MODEL_PATH = "sh.rnnn"

def denoise_with_rnnoise(input_file: str, output_file: str, model_path: str = RNNOISE_MODEL_PATH) -> None:
    """
    Применяет шумоподавление к аудиофайлу с использованием RNNoise.
    """
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Модель RNNoise не найдена: {model_path}")

    logger.info(f"Начало шумоподавления: {input_file} → {output_file}")
    try:
        (
            ffmpeg
            .input(input_file)
            .filter('arnndn', m=model_path)
            .output(output_file)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        logger.info(f"Шумоподавление завершено: {output_file}")
    except ffmpeg.Error as e:
        err = e.stderr.decode('utf-8', errors='ignore')
        logger.error(f"Ошибка FFmpeg при шумоподавлении:\n{err}")
        raise

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Обрабатывает POST-запрос с аудиофайлом, выполняет шумоподавление и транскрипцию.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не предоставлен'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Имя файла не указано'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_path = os.path.join(tmpdir, 'input.ogg')
            denoised_path = os.path.join(tmpdir, 'denoised.wav')

            # Сохранение загруженного файла
            file.save(raw_path)
            logger.info(f"Файл сохранён: {raw_path}")

            # Применение шумоподавления
            denoise_with_rnnoise(raw_path, denoised_path)

            # Загрузка модели Whisper
            logger.info("Загрузка модели Whisper...")
            model = transcribe_with_denoise.load_model('small')
            logger.info("Модель Whisper загружена.")

            # Выполнение транскрипции
            logger.info("Начало транскрипции...")
            result = model.transcribe(denoised_path, language='ru')
            logger.info("Транскрипция завершена.")

            return jsonify({'text': result['text']})

    except Exception as e:
        logger.exception("Ошибка при обработке запроса:")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4344, debug=True)
