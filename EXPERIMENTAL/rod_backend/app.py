import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.services.stt_service import speech_to_text
from src.services.tts_service import text_to_speech
from src.services.textgen_service import get_rod_response
from src.services.memory_service import append_memory, load_memory

app = FastAPI()

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
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp:
        temp_path = Path(temp.name)