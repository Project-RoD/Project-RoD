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

time_start = time.time()

def speech_to_text(inpath, outpath, api_key):
    client = OpenAI(api_key=API_KEY)
    AUDIO_DIR = FILE_PATH / inpath
    OUTPUT_DIR = FILE_PATH / outpath
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    EXTS = (".m4a", ".mp3", ".wav")
    results = []

    for filename in os.listdir(AUDIO_DIR):
        if filename.lower().endswith(EXTS):
            filepath = AUDIO_DIR / filename
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
                out_file = OUTPUT_DIR / f"{Path(filename).stem}.txt"
                out_file.write_text(text, encoding="utf-8")

                results.append({
                    "filename": filename,
                    "transcript_path": str(out_file),
                    "text": text
                })
            finally:
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception as e:
                        print(f"Warning: Couldnt delete {temp_path}: {e}")
    return results

speech_to_text("audio_files", "transcript", API_KEY)
time_end = time.time()
time_check = time_end - time_start
print(f"It took {time_check} seconds.")