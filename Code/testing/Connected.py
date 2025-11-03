import os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent[1]

sys.path.append(BASE_DIR / "whisper_test")
sys.path.append(BASE_DIR / "grammar_check_test")