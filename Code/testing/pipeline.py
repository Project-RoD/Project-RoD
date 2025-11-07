import os, sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from speech_to_text.whisper_test import speech_to_text
from speech_to_text.grammar_check_test import check_grammar
from text_generation.openai_api import generate_reply
from text_to_speech.text_to_speech import text_to_speech_device
from memory_manager import append_memory

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent[1]
MEMORY_FILE = Path(__file__).parent / "memory.jsonl"

def process(audio_file):
    text = speech_to_text(audio_file)
    append_memory("user", text)

    grammar = check_grammar(text)
    append_memory("grammar_feedback")

    reply = generate_reply(text)

    audio_path = text_to_speech_device(reply)
    return {
        "user_text": text,
        "grammar_feedback": grammar,
        "reply_text": reply,
        "reply_audio": audio_path
    }