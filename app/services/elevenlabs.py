import os 
import random
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API")
    )

PREMADE_VOICES = [
    'pNInz6obpgDQGcFmaJgB', # Adam
    'Xb7hH8MSUJpSbSDYk0k2', # Alice
    'pqHfZKP75CvOlQylNhV4', # Bill
    'nPczCjzI2devNBz1zQrb', # Brian
    'IKne3meq5aSn9XLyUdCD', # Charlie
    'onwK4e9ZLuTAKqWW03F9', # Daniel
    ]

VOICE_MAPPING = {
    "Adam": "pNInz6obpgDQGcFmaJgB", 
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Bill": "pqHfZKP75CvOlQylNhV4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Daniel": "onwK4e9ZLuTAKqWW03F9", 
}

def random_voice() -> str:

    voice_id = random.choice(PREMADE_VOICES)
    return voice_id 
    

def generate_tts(text: str, output_dir: Path, voice_id: str = "random"):
   
    if voice_id == "random":
        voice_id = random_voice()
        print(f"Random voice selected: {voice_id}")

    try:
        response = elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
        )

        filename = f"tts_{uuid4().hex[:8]}.mp3"
        file_path = output_dir / filename


        with open(file_path, 'wb') as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
        print(f"Voice successfully saved")
        return file_path
    except Exception as e:
        raise RuntimeError(f"Elevenlabs critical error: {e}")