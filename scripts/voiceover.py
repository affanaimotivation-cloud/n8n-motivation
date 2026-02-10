from gtts import gTTS
import os

def create_voice(text, output_path="voice.mp3", lang="hi"):
    """
    Hindi voiceover create karta hai
    """
    if not text:
        raise ValueError("Text empty hai, voice nahi ban sakti")

    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)

    if not os.path.exists(output_path):
        raise RuntimeError("Voice file create nahi hui")

    return output_path
