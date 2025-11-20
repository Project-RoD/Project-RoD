import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import aiofiles
import uuid

# Import your brains
from src.services.textgen_service import get_rod_response
from src.services.stt_service import speech_to_text
from src.services.tts_service import text_to_speech
import src.services.db_service as db

app = FastAPI()

# Pydantic Models (Defines JSON data shape)
class UserMessage(BaseModel):
    user_id: str
    message: str
    # If this is set, we are locking context (User clicked "Discuss" in Media Hub)
    context_data: Optional[dict] = None

class SynthesisRequest(BaseModel):
    text: str

# LIFECYCLE
@app.on_event("startup")
async def startup_event():
    """Initialize the Database when server starts."""
    print("Checking database...")
    db.init_db()

# STATIC FILES
AUDIO_DIR = Path.cwd() / "src" / "assets" / "audio"
# Create if it doesn't exist, to avoid crash
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")


# ENDPOINTS
@app.post("/chat")
async def handle_chat(request: UserMessage):
    """
    The Main Brain. 
    1. Ensures user exists.
    2. Finds/Creates the conversation thread.
    3. Saves user message to DB.
    4. Generates AI response using full DB history.
    5. Saves AI response to DB.
    """
    user_id = request.user_id
    text_input = request.message.strip()

    # 1. Ensure User Exists
    db.create_user_if_not_exists(user_id)

    # 2. Handle Conversation Thread
    # Check if we need to start a fresh context (Media Hub Button)
    if request.context_data:
        print(f"Starting NEW conversation with Context: {request.context_data}")
        conversation_id = db.start_new_conversation(user_id, request.context_data)
    else:
        # Resume existing or start new if none exists
        conversation_id = db.get_latest_conversation_id(user_id)
        if not conversation_id:
            print("No active conversation found. Starting new.")
            conversation_id = db.start_new_conversation(user_id)

    # 3. Save User Message
    db.add_message(conversation_id, "user", text_input)

    # 4. Fetch History & Generate Response
    # We retrieve the conversation history from SQL to send to GPT
    history_dicts = db.get_chat_history(conversation_id)
    
    # (Optional: Inject Media Context into System Prompt here if needed later)
    
    response_text = await get_rod_response(history_dicts) or "Beklager, jeg forsto ikke det."

    # 5. Save AI Response
    db.add_message(conversation_id, "assistant", response_text)

    # Return the single response (Frontend appends it to UI)
    return {"role": "assistant", "content": response_text}


@app.post("/transcribe")
async def handle_transcription(audio_file: UploadFile = File(...)):
    """
    Standard Whisper implementation. 
    """
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


@app.post("/synthesize")
async def handle_synthesis(request: SynthesisRequest, req: Request):
    """
    Standard ElevenLabs implementation.
    """
    filename = f"{uuid.uuid4()}.mp3"
    audio_path = await text_to_speech(request.text, filename=filename)
    
    if audio_path:
        file_url = f"{req.base_url}audio/{filename}"
        return {"url": file_url}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate audio")
    

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """
    Returns the list of past conversations for the burger menu.
    """
    conversations = db.get_user_conversations(user_id)
    return {"conversations": conversations}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)