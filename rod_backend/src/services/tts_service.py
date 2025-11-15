import os
from dotenv import load_dotenv
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import save
import asyncio
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = AsyncElevenLabs(api_key=API_KEY)

# Resource Folder
# Create a dedicated folder for audio files inside resources
AUDIO_OUTPUT_DIR = Path.cwd() / "src" / "assets" / "audio"
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _save_audio_sync(audio_bytes: bytes, output_path: str):
    """Synchronous function to save bytes to a file."""
    try:
        save(audio_bytes, output_path)
    except Exception as e:
        print(f"Error saving audio file: {e}")

async def text_to_speech(chat_text: str, filename="output.mp3"):
    """
    Asynchronously converts text to speech using ElevenLabs and saves it.
    Returns the Path to the saved file.
    """
    print("Generating speech...")
    try:
        audio_stream = client.text_to_speech.convert(
            voice_id="s2xtA7B2CTXPPlJzch1v",
            model_id="eleven_flash_v2_5",
            text=chat_text,
            output_format="mp3_44100_128"
        )
        
        # Iterate over the stream to collect the bytes
        audio_bytes = b""
        async for chunk in audio_stream:
            audio_bytes += chunk

        output_path = AUDIO_OUTPUT_DIR / filename
        
        await asyncio.to_thread(_save_audio_sync, audio_bytes, str(output_path))
        
        print(f"Audio saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"ElevenLabs API error: {e}")
        return None