import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import aiofiles
import uuid

# Import your brains
import src.services.db_service as db
from src.services.textgen_service import get_rod_response
from src.services.stt_service import speech_to_text
from src.services.tts_service import text_to_speech
from src.services.grammar_check_service import analyze_grammar

app = FastAPI()

# Pydantic Models (Defines JSON data shape)
class LevelUpdate(BaseModel):
    user_id: str
    level: str # 'A1', 'A2', 'B1'

class UserMessage(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[int] = None
    context_data: Optional[dict] = None
    force_new: bool = False

class SynthesisRequest(BaseModel):
    text: str

class TitleUpdate(BaseModel):
    title: str


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
@app.get("/user/streak/{user_id}")
async def get_streak(user_id: str):
    streak = db.get_user_streak(user_id)
    return {"streak": streak}

@app.post("/user/level")
async def update_level(data: LevelUpdate):
    """Updates the user's proficiency level."""
    print(f"Setting user {data.user_id} to level {data.level}")
    db.set_user_level(data.user_id, data.level)
    return {"status": "success", "level": data.level}

@app.get("/feedback/{conversation_id}")
async def get_conversation_feedback(conversation_id: int):
    """Returns a list of grammar corrections for a specific chat."""
    return {"feedback": db.get_feedback_for_conversation(conversation_id)}

async def run_grammar_check(msg_id: int, history: List[Dict], user_text: str, ai_response: str, level: str):
    """
    Background Task: Checks grammar without blocking the chat.
    """
    print(f"🕵️ Checking grammar for: {user_text}")
    result = await analyze_grammar(history, user_text, ai_response, level)
    
    if result and result.get("has_error"):
        print(f"🚩 Feedback Generated ({level})")
        # Save to DB so the user can see it later in the feedback menu
        db.add_feedback(msg_id, user_text, result["correction"], result["explanation"])
    else:
        print("✅ Message looks good.")

@app.post("/chat")
async def handle_chat(request: UserMessage, background_tasks: BackgroundTasks):
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
    db.update_user_streak(user_id)

    # 2. Determine Conversation ID
    if request.force_new or request.context_data:
        print("Starting NEW conversation")
        conversation_id = db.start_new_conversation(user_id, request.context_data)
    elif request.conversation_id:
        conversation_id = request.conversation_id
        print(f"Resuming conversation ID: {conversation_id}")
    else:
        conversation_id = db.get_latest_conversation_id(user_id)
        if not conversation_id:
            conversation_id = db.start_new_conversation(user_id)

    # 3. Save User Message & Trigger Grammar Check
    msg_id = db.add_message(conversation_id, "user", text_input)

    # 4. Fetch History & Generate Response
    history_dicts = db.get_chat_history(conversation_id)

    # 5. Generate Response
    user_level = db.get_user_level(user_id)
    print(f"Generating response for level: {user_level}")
    response_text = await get_rod_response(history_dicts, level=user_level) or "Beklager, jeg forsto ikke det."

    # 6. Save AI Response
    db.add_message(conversation_id, "assistant", response_text)

    # 7. Trigger Background Check
    # We pass 'history_dicts[:-1]' to remove the current message from the "History" context block
    context_history = history_dicts[:-1] 
    
    background_tasks.add_task(
        run_grammar_check, 
        msg_id, 
        context_history, 
        text_input,     
        response_text,
        user_level 
    )

    return {
        "role": "assistant", 
        "content": response_text, 
        "conversation_id": conversation_id 
    }


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
    
@app.get("/chat/{conversation_id}")
async def get_conversation_messages(conversation_id: int):
    """Loads the actual messages for a specific thread."""
    history = db.get_chat_history(conversation_id)
    return {"messages": history}

@app.patch("/conversations/{conversation_id}")
async def update_title(conversation_id: int, update: TitleUpdate):
    """Renames a conversation."""
    db.update_conversation_title(conversation_id, update.title)
    return {"status": "success"}

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """
    Returns the list of past conversations for the burger menu.
    """
    conversations = db.get_user_conversations(user_id)
    return {"conversations": conversations}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)