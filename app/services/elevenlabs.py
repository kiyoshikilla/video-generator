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

_VOICE_CACHE = {}

VOICE_MAPPING = {
    "Adam": "pNInz6obpgDQGcFmaJgB", 
    "Alice": "Xb7hH8MSUJpSbSDYk0k2",
    "Bill": "pqHfZKP75CvOlQylNhV4",
    "Brian": "nPczCjzI2devNBz1zQrb",
    "Charlie": "IKne3meq5aSn9XLyUdCD",
    "Daniel": "onwK4e9ZLuTAKqWW03F9", 
}

def refresh_voice_cache():
    global _VOICE_CACHE
    try:
        print("Refreshing the list of voices from Elevenlabs")
        response = elevenlabs.voices.get_all()
        
        new_cache = {}
        for voice in response.voices:
            new_cache[voice.name.lower()] = voice.voice_id
            
        _VOICE_CACHE = new_cache
        print(f"Successfully loaded {len(_VOICE_CACHE)} voices to the cache.")
        
    except Exception as e:
        print(f"Cant get a list of voices: {e}. Using the standart list.")
        for name, vid in VOICE_MAPPING.items():
            _VOICE_CACHE[name.lower()] = vid

def get_voice_id(voice_input: str) -> str:

    if not _VOICE_CACHE:
        refresh_voice_cache()

    input_lower = voice_input.lower()

    if input_lower == "random":
        if _VOICE_CACHE:
            random_name = random.choice(list(_VOICE_CACHE.keys()))
            return _VOICE_CACHE[random_name]
        return VOICE_MAPPING["Adam"]

    if input_lower in _VOICE_CACHE:
        return _VOICE_CACHE[input_lower]
    
    return voice_input

def random_voice() -> str:

    voice_id = random.choice(VOICE_MAPPING)
    return voice_id 
    

def generate_tts(text: str, output_dir: Path, voice_id: str = "random"):
   
    try:

        real_voice_id = get_voice_id(voice_id)
    
        response = elevenlabs.text_to_speech.convert(
            voice_id=real_voice_id,
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
        print(f"Elevenlabs error (Voice - {voice_id}: {e})")
        return None