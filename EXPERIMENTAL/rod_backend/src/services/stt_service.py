import os
import asyncio
import ffmpeg
import tempfile
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=API_KEY)

def _convert_to_wav_sync(filepath: Path) -> Optional[str]:
    """
    Synchronous (blocking) function to convert audio file to WAV.
    This MUST be run in a separate thread.
    """
    print(f"Starting audio conversion for {filepath}...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_path = temp.name
    
    try:
        (
            ffmpeg
            .input(str(filepath))
            .output(temp_path, ar=16000, ac=1, format='wav')
            .overwrite_output()
            .run(quiet=True)
        )
        print("Audio converted.")
        return temp_path
    except Exception as e:
        print(f"FFMPEG error: {e}")
        return None
    
async def speech_to_text(filepath: Path) -> str:
    """
    Asynchronously converts an audio file to text using Whisper.
    """
    EXTS = (".m4a", ".mp3", ".wav", ".aac", ".ogg") # Common audio formats
    if not filepath.suffix.lower() in EXTS:
        return "Unsupported audio format."

    print(f"Transcribing {filepath}...")
    
    # Run the blocking FFMPEG conversion in a separate thread
    wav_path_str = await asyncio.to_thread(_convert_to_wav_sync, filepath)
    
    if not wav_path_str:
        return "Error converting audio."

    wav_path = Path(wav_path_str)
    try:
        # Now that we have the file, open it and call the async API
        with open(wav_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        text = transcript.text.strip()
        print(f"Transcription: {text}")
        return text
    except Exception as e:
        print(f"Whisper API error: {e}")
        return "Error transcribing audio."
    finally:
        # Clean up the temporary WAV file
        if wav_path.exists():
            try:
                wav_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {wav_path}: {e}")