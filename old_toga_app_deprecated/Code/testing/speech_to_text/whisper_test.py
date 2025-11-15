import os, subprocess, tempfile
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time
"""
import whisper

model = whisper.load_model("base")
"""
#Might move this code below to a different File, so i can use it


FILE_PATH = Path(__file__).parent.resolve()

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
print("Key loaded?", os.getenv("OPENAI_API_KEY"))

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

def speech_to_text(filename):
    EXTS = (".m4a", ".mp3", ".wav")

    if not filename.suffix.lower() in EXTS:
        raise ValueError(f"Unsupported format: {filename}")

    filepath = Path(filename)
    print(f"Transcribing {filename}...")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_path = Path(temp.name)

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(filepath), "-ar", "16000", "-ac", "1", str(temp_path)],
            check= True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
                
        text = transcript.text.strip()
        return text


    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                print(f"Warning: Couldnt delete {temp_path}: {e}")

if __name__ == "__main__":
    AUDIO_DIR = FILE_PATH / "audio_files"
    OUTPUT_DIR = FILE_PATH / "transcript"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for audio in AUDIO_DIR.iterdir():
        time_start = time.time()
        results = speech_to_text(audio)
        time_end = time.time()
        
        out_file = OUTPUT_DIR / f"{audio.stem}.txt"
        out_file.write_text(results, encoding="utf-8")
        print(f"Saved to {audio.name} -> {out_file}")

    time_check = time_end - time_start
    print(f"It took {time_check} seconds.")