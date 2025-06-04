# file: transcribe_with_denoise.py
import ffmpeg
import whisper
import os

# Путь к файлу модели RNNoise: скачайте из репозитория https://github.com/GregorR/rnnoise-models
RNNOISE_MODEL_PATH = "sh.rnnn"

def transcribe_with_denoise(input_file: str,
                             whisper_model: str = 'small',
                             language: str = 'ru') -> str:
    """
    Выполняет шумоподавление файла через встроенную модель RNNoise и транскрибирует результат с помощью Whisper.

    Args:
        input_file: путь до исходного аудиофайла.
        whisper_model: имя модели Whisper ('tiny', 'base', 'small', 'medium', 'large').
        language: язык распознавания (ISO-код).

    Returns:
        Распознанный текст.

    Raises:
        FileNotFoundError: если модель RNNoise не найдена.
        ffmpeg.Error: при ошибках FFmpeg.
    """
    if not os.path.isfile(RNNOISE_MODEL_PATH):
        raise FileNotFoundError(f"Модель RNNoise не найдена: {RNNOISE_MODEL_PATH}")

    # временный файл для шумоподавленного аудио
    base, _ = os.path.splitext(input_file)
    denoised_file = f"{base}_denoised.wav"

    # 1) Шумоподавление
    try:
        (
            ffmpeg
            .input(input_file)
            .filter('arnndn', m=RNNOISE_MODEL_PATH)
            .output(denoised_file, **{'y': None})
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        err = e.stderr.decode('utf-8', errors='ignore')
        raise RuntimeError(f"Ошибка FFmpeg при шумоподавлении: {err}")

    # 2) Транскрипция
    model = whisper.load_model(whisper_model)
    #result = model.transcribe(denoised_file, language=language)
    result = model.transcribe(input_file, language=language)
    text = result.get('text', '').strip()

    # удалить временный файл
    try:
        os.remove(denoised_file)
    except OSError:
        pass

    return text



