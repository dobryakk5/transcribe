import whisper
import soundfile as sf
import librosa
import numpy as np
import logging

logger = logging.getLogger(__name__)

def transcribe_v(input_file: str,
                 whisper_model: str = 'small',
                 language: str = 'ru') -> str:
    # 1. Чтение и ресемплинг
    data, sr = sf.read(input_file)
    if sr != 16000:
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        sr = 16000
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 2. Логирование длительности и уровня
    duration = len(data) / sr
    max_amp = float(np.max(np.abs(data)))
    logger.info(f"Audio duration: {duration:.2f}s, max amplitude: {max_amp:.3f}")

    # 3. Нормализация
    if max_amp > 0:
        data = data / max_amp

    # 4. Приведение к float32
    data = data.astype(np.float32)

    # 5. Транскрипция с пониженными порогами
    model = whisper.load_model(whisper_model)
    result = model.transcribe(
        data,
        language=language,
        fp16=False,
        temperature=0,
        no_speech_threshold=0.3,
        logprob_threshold=-1.0
    )

    transcription = result.get("text", "").strip()
    logger.info(f"Whisper returned transcription: {transcription!r}")
    return transcription
