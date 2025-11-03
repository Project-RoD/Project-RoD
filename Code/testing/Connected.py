import os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/bretski/Documents/Project-RoD/Code/rod/tests/.env")

BASE_DIR = Path(__file__).resolve().parent[1]

sys.path.append(str(BASE_DIR / "whisper_test"))
sys.path.append(str(BASE_DIR / "grammar_check_test"))

import whisper_test
import gramma_check_test