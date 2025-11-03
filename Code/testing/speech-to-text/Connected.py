import os, sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from whisper_test import 
from grammar_check_test import check_grammar

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent[1]
