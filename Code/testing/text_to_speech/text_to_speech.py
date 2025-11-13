import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import time
from pathlib import Path

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))
print("Loaded key:", os.getenv("ELEVEN_LABS_API_KEY"))

text = "Hei! Eg er glad i brunost. Har du ete i dag?"

def text_to_speech_device(chat_text, filename = "output.mp3"):
    from elevenlabs import save

    audio = client.text_to_speech.convert(
        voice_id="s2xtA7B2CTXPPlJzch1v",
        model_id="eleven_flash_v2_5",
        text=chat_text,
        output_format="mp3_44100_128"
    )

    save(audio, filename)
    return filename

time_start = time.time()
text_to_speech_device(text)
time_end = time.time()
time_test = time_end - time_start

print(time_test)
