import ffmpeg
import transcribe_with_denoise
import os


def denoise_with_afftdn(input_file: str, output_file: str, noise_reduction: int = 15) -> None:
    """
    Шумоподавление с помощью FFmpeg и фильтра afftdn.
    """
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, af=f'afftdn=nr={noise_reduction}')
            .overwrite_output()
            .run()
        )
        print(f"[afftdn] {input_file} → {output_file}")
    except ffmpeg.Error as e:
        print("❌ Ошибка FFmpeg при шумоподавлении:")
        print(e.stderr.decode())
        raise


def transcribe_audio(audio_path: str, language: str = 'ru', model_size: str = 'small') -> str:
    """
    Распознаёт речь из файла с помощью Whisper.
    """
    model = transcribe_with_denoise.load_model(model_size)
    result = model.transcribe(audio_path, language=language)
    return result['text']


if __name__ == '__main__':
    # Пути к файлам
    raw_audio = 'audio.ogg'          # входной файл
    denoised_audio = 'denoised.wav'  # результат после afftdn

    # 1) Подавление шума
    denoise_with_afftdn(raw_audio, denoised_audio)

    # 2) Распознавание речи
    text = transcribe_audio(denoised_audio)
    print("📄 Распознанный текст:")
    print(text)
