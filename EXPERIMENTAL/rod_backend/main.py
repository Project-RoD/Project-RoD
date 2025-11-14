# in backend/main.py
import uvicorn
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import aiofiles

# Import your brains
from src.services.stt_service import speech_to_text
from src.services.textgen_service import get_rod_response
from src.services.tts_service import text_to_speech
from src.services.memory_service import load_memory, append_memory

app = FastAPI()

# --- Pydantic Models (Defines JSON data shape) ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    history: List[ChatMessage]

class SynthesisRequest(BaseModel):
    text: str

# --- 1. Text Chat Endpoint ---
@app.post("/chat")
async def handle_chat(chat_data: ChatHistory):
    # Convert Pydantic models to simple dicts for your service
    history_dicts = [msg.dict() for msg in chat_data.history]
    
    # Get response from your existing service
    response_text = await get_rod_response(history_dicts)
    
    # Save to memory
    await append_memory("assistant", response_text)
    
    return {"role": "assistant", "content": response_text}

# --- 2. Speech-to-Text (STT) Endpoint ---
@app.post("/transcribe")
async def handle_transcription(audio_file: UploadFile = File(...)):
    # This is the tricky part. We must save the uploaded file temporarily
    # so ffmpeg (inside your stt_service) can read it.
    
    # Use a temp path
    temp_path = Path(f"temp_{audio_file.filename}")
    
    try:
        # Asynchronously write the uploaded file to disk
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await audio_file.read()
            await out_file.write(content)
        
        # Now, call your existing service function on the file
        transcribed_text = await speech_to_text(temp_path)
        
        return {"text": transcribed_text}
    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"error": str(e)}
    finally:
        # Clean up the temp file
        if temp_path.exists():
            temp_path.unlink()

# --- 3. Text-to-Speech (TTS) Endpoint ---
@app.post("/synthesize")
async def handle_synthesis(request: SynthesisRequest):
    # Call your existing service
    audio_path = await text_to_speech(request.text, filename="demo_output.mp3")
    
    if audio_path:
        # For the demo, the simplest way is to just tell the frontend
        # where to download the file *from the server*.
        # This requires more setup (StaticFiles).
        #
        # A much, MUCH simpler way for the demo:
        # Just return the filename. The frontend will then have to
        # make a *separate* request to download that file.
        #
        # Let's keep it simple and just return the *path*
        # (This is a complex topic, but for now, just generate the file)
        return {"filename": str(audio_path)}
    else:
        return {"error": "Failed to generate audio"}
        
# --- Command to run this server ---
# In your terminal, run:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000