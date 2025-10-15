# speech/text_to_speech.py
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

import platform
import time
from gtts import gTTS

class TextToSpeech:
    def __init__(self):
        pass
    
    def speak(self, text):
        """Speak with gTTS and also print to console."""
        print("🤖 Friday says:", text)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_path = f.name
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            self._play_audio(temp_path)
            time.sleep(0.2)
        except Exception as e:
            print(f"❌ Error playing TTS: {e}")
        finally:
            self._cleanup_temp_file(temp_path)
    
    def _play_audio(self, file_path):
        """Play audio file based on OS"""
        system = platform.system()
        if system == "Linux":
            os.system(f"mpg123 -q {file_path} || aplay {file_path} || paplay {file_path}")
        elif system == "Darwin":
            os.system(f"afplay {file_path}")
        elif system == "Windows":
            os.startfile(file_path)
    
    def _cleanup_temp_file(self, file_path):
        """Clean up temporary audio file"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
