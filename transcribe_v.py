import whisper
import soundfile as sf
import librosa
import numpy as np

def transcribe_v(input_file, whisper_model="small", language="ru"):
    # 1. Читаем OGG
    data, sr = sf.read(input_file)

    # 2. Убедимся в формате: моно 16000 Гц
    if sr != 16000:
        data = librosa.resample(data,
                                orig_sr=sr,
                                target_sr=16000)
        sr = 16000
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # 3. Передаём массив напрямую (если поддерживает ваша версия)
    model = whisper.load_model(whisper_model)
    result = model.transcribe(data, language=language, samplerate=sr)
    return result.get("text", "").strip()
