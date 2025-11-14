import tempfile, uvicorn
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.services.stt_service import speech_to_text
from src.services.tts_service import text_to_speech
from src.services.textgen_service import get_rod_response
from src.services.memory_service import append_memory, load_memory

app = FastAPI()

#Small fix to make the tts function properly
AUDIO_DIR = Path.cwd() / "src" / "assets" / "audio"
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

#Setting up middleware for communication to browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#main app 
@app.post("/core_function")
async def core_function(file: UploadFile = File(...)):
    #Save the incoming file temporarily
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp:
        temp_path = Path(temp.name)
        temp.write(await file.read())
    
    try:
        # Transcribes Audio
        user_text = await speech_to_text(temp_path)
        await append_memory("user", user_text)

        history = await load_memory()
        ai_reply = await get_rod_response(history)
        await append_memory("assistant", ai_reply)

        audio_path = await text_to_speech(ai_reply)
        print("👉 TTS returned:", audio_path)
        audio_filename = Path(audio_path).name

        return {
           "user_text": user_text,
           "assistant_text": ai_reply,
           "reply_audio_url": f"/audio/{audio_filename}"
        }
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                print(f"Couldn't delete the temp file {temp_path}: {e}")