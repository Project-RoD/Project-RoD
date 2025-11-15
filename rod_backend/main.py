import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from pathlib import Path
import aiofiles
import uuid

# Import your brains
from src.services.textgen_service import get_rod_response
from src.services.stt_service import speech_to_text
from src.services.tts_service import text_to_speech
from src.services.memory_service import load_memory, append_memory

app = FastAPI()

# Pydantic Models (Defines JSON data shape)
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    history: List[ChatMessage]

class SynthesisRequest(BaseModel):
    text: str

# Mount Static Directory
# This makes the 'src/rod/resources/audio' folder publicly accessible at the URL path '/audio'
AUDIO_DIR = Path.cwd() / "src" / "assets" / "audio"
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")


# 1. Text Chat Endpoint
@app.post("/chat")
async def handle_chat(chat_data: ChatHistory):
    history_dicts = [msg.dict() for msg in chat_data.history]
    response_text = await get_rod_response(history_dicts)
    await append_memory("assistant", response_text)
    return {"role": "assistant", "content": response_text}

# 2. Speech-to-Text (STT) Endpoint
@app.post("/transcribe")
async def handle_transcription(audio_file: UploadFile = File(...)):
    temp_path = Path(f"temp_{audio_file.filename}")
    try:
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await audio_file.read()
            await out_file.write(content)
        
        transcribed_text = await speech_to_text(temp_path)
        return {"text": transcribed_text}
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"error": str(e)}
    finally:
        if temp_path.exists():
            temp_path.unlink()

# 3. Text-to-Speech (TTS) Endpoint
@app.post("/synthesize")
async def handle_synthesis(request: SynthesisRequest, req: Request): # Add 'req: Request'
    # Generate a unique filename to prevent overwrites
    filename = f"{uuid.uuid4()}.mp3"
    
    # Call your existing service with the new filename
    audio_path = await text_to_speech(request.text, filename=filename)
    
    if audio_path:
        # Construct the full, public URL for the file
        file_url = f"{req.base_url}audio/{filename}"
        
        # Return the URL in the JSON response
        return {"url": file_url}
    else:
        # Return a proper server error
        raise HTTPException(status_code=500, detail="Failed to generate audio")