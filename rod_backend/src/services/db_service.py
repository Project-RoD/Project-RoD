import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

# Define the database file location
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "rod.db"

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Initializes the database tables."""
    print(f"Initializing Database at: {DB_FILE}")
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        proficiency_level TEXT DEFAULT 'A1',
        streak_days INTEGER DEFAULT 0,
        last_active_date TEXT,
        created_at TEXT
    )
    """)

    # 2. Conversations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        context_lock TEXT, 
        title TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # 3. Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        role TEXT,
        content TEXT,
        created_at TEXT,
        FOREIGN KEY(conversation_id) REFERENCES conversations(id)
    )
    """)

    # 4. Feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER,
        user_text TEXT,
        correction TEXT,
        explanation TEXT,
        created_at TEXT,
        FOREIGN KEY(message_id) REFERENCES messages(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database Initialized")


# USER FUNCTIONS
def create_user_if_not_exists(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (id, created_at) VALUES (?, ?)", 
                       (user_id, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        conn.close()

def set_user_level(user_id: str, level: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (id, proficiency_level, created_at) 
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET proficiency_level=excluded.proficiency_level
        """, (user_id, level, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()

def get_user_level(user_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT proficiency_level FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row and row['proficiency_level']:
        return row['proficiency_level']
    return 'A1'

def update_user_streak(user_id: str):
    """
    Updates streak based on activity. 
    Rules:
    - Active today? Do nothing.
    - Active yesterday? Streak + 1.
    - Inactive for > 1 day? Reset to 1.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current state
    row = cursor.execute("SELECT streak_days, last_active_date FROM users WHERE id = ?", (user_id,)).fetchone()
    
    today_str = datetime.now().date().isoformat()
    
    if not row:
        create_user_if_not_exists(user_id)
        current_streak = 1
    else:
        last_date_str = row['last_active_date']
        current_streak = row['streak_days'] or 0
        
        if last_date_str == today_str:
            # Already active today, do nothing
            conn.close()
            return
        
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str).date()
            delta = (datetime.now().date() - last_date).days
            
            if delta == 1:
                # Was active yesterday -> Increment
                current_streak += 1
            else:
                # Missed a day (or more) -> Reset
                current_streak = 1
        else:
            # First time active
            current_streak = 1

    # Save updates
    cursor.execute("UPDATE users SET streak_days = ?, last_active_date = ? WHERE id = ?", 
                   (current_streak, today_str, user_id))
    conn.commit()
    conn.close()

def get_user_streak(user_id: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT streak_days FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row['streak_days'] if row else 0


# CONVERSATION FUNCTIONS
def start_new_conversation(user_id: str, context_data: Optional[dict] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    context_str = json.dumps(context_data) if context_data else None
    
    cursor.execute("""
        INSERT INTO conversations (user_id, context_lock, created_at) 
        VALUES (?, ?, ?)
    """, (user_id, context_str, datetime.now().isoformat()))
    
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id or 0

def get_latest_conversation_id(user_id: str) -> Optional[int]:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("""
        SELECT id FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()
    return row['id'] if row else None

def get_conversation_context(conversation_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT context_lock FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
    conn.close()
    if row and row['context_lock']:
        return json.loads(row['context_lock'])
    return None

def update_conversation_title(conversation_id: int, new_title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conversation_id))
    conn.commit()
    conn.close()

def get_user_conversations(user_id: str) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, title, created_at FROM conversations WHERE user_id = ? ORDER BY created_at DESC"
    rows = cursor.execute(query, (user_id,)).fetchall()
    
    results = []
    for row in rows:
        display_title = row["title"]
        
        if not display_title:
            # Fallback: Fetch first user message
            msg_row = cursor.execute(
                "SELECT content FROM messages WHERE conversation_id = ? AND role = 'user' LIMIT 1", 
                (row["id"],)
            ).fetchone()
            
            if msg_row and msg_row["content"]:
                display_title = (msg_row["content"][:30] + '...') if len(msg_row["content"]) > 30 else msg_row["content"]
            else:
                display_title = "Ny Samtale"

        results.append({
            "id": row["id"],
            "date": row["created_at"],
            "title": display_title
        })

    conn.close()
    return results


# MESSAGE & FEEDBACK FUNCTIONS
def add_message(conversation_id: int, role: str, content: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, role, content, datetime.now().isoformat()))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id or 0

def get_chat_history(conversation_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY id ASC
    """, (conversation_id,)).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]

def add_feedback(message_id: int, user_text: str, correction: str, explanation: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (message_id, user_text, correction, explanation, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (message_id, user_text, correction, explanation, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_feedback_for_conversation(conversation_id: int) -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.user_text, f.correction, f.explanation, f.created_at 
        FROM feedback f
        JOIN messages m ON f.message_id = m.id
        WHERE m.conversation_id = ?
        ORDER BY f.created_at DESC
    """
    rows = cursor.execute(query, (conversation_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]