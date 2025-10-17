import os, subprocess
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
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

MODEL = "whisper-1"

AUDIO_DIR = FILE_PATH / "audio_files"
OUTPUT_DIR = FILE_PATH / "transcript"
os.makedirs(OUTPUT_DIR, exist_ok=True)

EXTS = (".m4a", ".mp3")

for filename in os.listdir(AUDIO_DIR):
    if filename.lower().endswith(EXTS):
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"Transcribing {filename}...")

        wav_path = os.path.join(AUDIO_DIR, f"{os.path.splitext(filename)[0]}.wav")

        #Run ffmpeg command
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", filepath,
            wav_path
        ], check=True)
    
        with open(wav_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model=MODEL,
                file=audio_file,
            )

        text = result.text.strip()
        outpath = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.txt")

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"Done  with {filename} and its now {outpath}")