import json
import asyncio
from datetime import datetime
from pathlib import Path

# This file will be created in project's root
MEMORY_FILE = Path.cwd() / "memory.jsonl"

def _append_memory_sync(role, content):
    """Synchronous function to write to file (to be run in a thread)."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "content": content
    }
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error appending memory: {e}")

def _load_memory_sync(limit=15):
    """Synchronous function to read from file (to be run in a thread)."""
    if not MEMORY_FILE.exists():
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        return [json.loads(l) for l in lines]
    except Exception as e:
        print(f"Error loading memory: {e}")
        return []

async def append_memory(role, content):
    """Asynchronously appends an entry to the memory file without blocking."""
    # asyncio.to_thread runs the blocking function in a separate thread
    await asyncio.to_thread(_append_memory_sync, role, content)

async def load_memory(limit=15):
    """Asynchronously loads messages from the memory file without blocking."""
    return await asyncio.to_thread(_load_memory_sync, limit)