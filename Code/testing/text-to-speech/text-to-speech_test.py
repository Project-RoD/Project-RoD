import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))

text = "Dette er en test melding."

def text_to_speech_device(chat_text, filename = "output.mp3"):
    from elevenlabs import save

    audio = client.text_to_speech.convert(
        voice_id="d6dMXDDMQ9zlhV3hOfx0",
        model_id="eleven_flash_v2_5",
        text=chat_text,
        output_format="mp3_44100_128"
    )

    save(audio, filename)
    return filename

text_to_speech_device(text)
