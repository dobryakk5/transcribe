import whisper

def transcribe_v(input_file: str,
               whisper_model: str = 'small',
               language: str = 'ru') -> str:
    """
    Выполняет транскрипцию аудиофайла с помощью Whisper.

    Args:
        input_file: путь до исходного аудиофайла.
        whisper_model: имя модели Whisper ('tiny', 'base', 'small', 'medium', 'large').
        language: язык распознавания (ISO-код).

    Returns:
        Распознанный текст.
    """
    model = whisper.load_model(whisper_model)
    result = model.transcribe(input_file, language=language)
    text = result.get('text', '').strip()
    return text