import whisper
import soundfile as sf
import numpy as np
import librosa

def transcribe_v(input_file, whisper_model="small", language="ru"):
    # 1. Читаем аудио
    data, sr = sf.read(input_file)
    if sr != 16000:
        data = librosa.resample(data, orig_sr=sr, target_sr=16000)
        sr = 16000
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    data = data.astype(np.float32)

    model = whisper.load_model(whisper_model)

    # 2. Конвертация в log-mel спектрограмму
    mel = whisper.log_mel_spectrogram(data).to(model.device)

    # 3. Декодирование
    options = whisper.DecodingOptions(language=language)
    result = whisper.decode(model, mel, options)
    return result.text.strip()
