import os
from pathlib import Path
import whisper

model = whisper.load_model("medium")
MODEL_DIR = Path(__file__).parent

AUDIO_DIR = MODEL_DIR/"audio_files"

OUTPUT_DIR = MODEL_DIR/"transcript"
os.makedirs(OUTPUT_DIR, exist_ok=True)

EXTS = (".m4a", ".mp3")

for filename in os.listdir(AUDIO_DIR):
    if filename.lower().endswith(EXTS):
        filepath = os.path.join(AUDIO_DIR, filename)
        print(f"Transcribing {filename}...")

        result = model.transcribe(filepath)
        text = result["text"].strip()

        outpath = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.txt")

        with open(outpath, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"Done  with {filename} and its now {outpath}")