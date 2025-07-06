import whisper
import soundfile as sf

def transcribe_v(input_file, whisper_model="small", language="ru"):
    data, samplerate = sf.read(input_file)
    # Whisper требует моно, 16000 Гц:
    import numpy as np
    if samplerate != 16000:
        import librosa
        data = librosa.resample(data, samplerate, 16000)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    model = whisper.load_model(whisper_model)
    result = model.transcribe(data, language=language, samplerate=16000)
    return result.get("text", "").strip()
