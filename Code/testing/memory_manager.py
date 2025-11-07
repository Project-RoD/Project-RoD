import json
import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.jsonl"

def append_memory(role, content):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content" : content
    }
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def load_memory(limit=15):
    if not MEMORY_FILE.exists():
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(l) for l in lines]