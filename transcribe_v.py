import os
import whisper
import soundfile as sf

def transcribe_v(input_file: str,
                 whisper_model: str = 'small',
                 language: str = 'ru') -> str:
    """
    Выполняет транскрипцию аудиофайла с помощью Whisper,
    предварительно конвертируя OGG → WAV через soundfile.
    """
    # 1. Конвертация OGG → WAV
    base, _ = os.path.splitext(input_file)
    wav_path = base + '.wav'

    # читаем OGG (libsndfile под капотом) и записываем WAV
    data, samplerate = sf.read(input_file)
    sf.write(wav_path, data, samplerate)

    # 2. Загрузка модели и транскрибирование
    model = whisper.load_model(whisper_model)
    result = model.transcribe(wav_path, language=language)
    text = result.get('text', '').strip()

    # 3. Очистка временного WAV
    try:
        os.remove(wav_path)
    except OSError:
        pass

    return text
