import os
from openai import OpenAI
from dotenv import load_dotenv
"""
import whisper

model = whisper.load_model("base")
"""
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

MODEL = "whisper-1"

AUDIO_DIR = "audio_files"
OUTPUT_DIR = "transcript"
os.makedirs(OUTPUT_DIR, exist_ok=True)

EXTS = (".m4a", ".mp3")

for filename in os.listdir(AUDIO_DIR):
    if filename.lower().endswith(EXTS):
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"Transcribing {filename}...")

    with open(filepath, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            model=MODEL,
            file=audio_file,
        )

        text = result["text"].strip()
        outpath = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.txt")

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"Done  with {filename} and its now {outpath}")