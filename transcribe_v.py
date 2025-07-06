import whisper
import soundfile as sf
import librosa
import numpy as np

def transcribe_v(input_file: str,
                 whisper_model: str = 'small',
                 language: str = 'ru') -> str:
    # 1. Читаем OGG
    data, sr = sf.read(input_file)  # обычно float64
    
    # 2. Ресемплируем к 16000 Гц, если нужно
    if sr != 16000:
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        sr = 16000
    
    # 3. Моно: усреднение каналов
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    
    # 4. Приводим к float32 и нормализуем
    data = data.astype(np.float32) / 32768.0  # формат PCM
    
    # 5. Транскрипция напрямую через Whisper
    model = whisper.load_model(whisper_model)
    result = model.transcribe(data, language=language, fp16=False)
    return result["text"].strip()
