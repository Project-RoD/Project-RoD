import os
import whisper

model = whisper.load_model("base")

AUDIO_DIR = "audio_jungle"

OUTPUT_DIR = "transcript"
#os.makedirs(OUTPUT_DIR, exist_ok=True)

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