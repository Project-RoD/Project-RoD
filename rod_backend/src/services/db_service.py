import sqlite3
import json
from pathlib import Path
from datetime import datetime 
from typing import List, Optional, Dict

# Define the database file location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "rod.db"

def get_connection():
    """ Establishes a connection to the SQLite database. """
    conn = sqlite3.connect(str(DB_FILE))
    # Make the rows behave like dicts
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """ Initializes the databse tables. """
    print(f"Initializing Database at: {DB_FILE}")
    conn = get_connection()
    cursor = conn.cursor()

    # Creates Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        created_at TEXT
    )
    """)

    # Creates Conversations Table
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

    # Creates Messages Table
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

    # Creates Feedback Table
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
    print("Database initialized")


# USER FUNCTIONS
def create_user_if_not_exists(user_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (id, created_at) VALUES (?, ?)", 
                       (user_id, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()


# CONVERSATION FUNCTIONS
def start_new_conversation(user_id: str, context_data: Optional[dict] = None) -> int:
    """
    Starts a new chat thread.
    context_data: If the user clicked 'Talk to Rod' on an article, 
    pass {'title': '...', 'summary': '...'} here.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # If we have media context, save it as a JSON string in the database
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
    """Finds the most recent chat thread for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    # Get the most recent conversation created by this user
    row = cursor.execute("""
        SELECT id FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()
    return row['id'] if row else None

def get_conversation_context(conversation_id: int) -> Optional[dict]:
    """Retrieves the media context (if any) for a specific thread."""
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT context_lock FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
    conn.close()
    
    if row and row['context_lock']:
        return json.loads(row['context_lock'])
    return None

def get_user_conversations(user_id: str) -> List[Dict]:
    """
    Returns a summary list of all conversations for the burger menu.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT c.id, c.created_at, 
               COALESCE(c.title, (SELECT content FROM messages m WHERE m.conversation_id = c.id AND m.role = 'user' LIMIT 1)) as display_title
        FROM conversations c
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    """
    
    rows = cursor.execute(query, (user_id,)).fetchall()
    conn.close()
    
    return [
        {
            "id": row["id"], 
            "date": row["created_at"], 
            "title": row["display_title"] or "New Conversation"
        } 
        for row in rows
    ]

def update_conversation_title(conversation_id: int, new_title: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conversation_id))
    conn.commit()
    conn.close()

# MESSAGE FUNCTIONS
def add_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, role, content, datetime.now().isoformat()))
    # Capture the ID of the message we just inserted
    msg_id = cursor.lastrowid 
    conn.commit()
    conn.close()
    return msg_id or 0

def get_chat_history(conversation_id: int) -> List[Dict]:
    """Fetches all messages for a specific thread."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY id ASC
    """, (conversation_id,)).fetchall()
    conn.close()

    # Convert to a list of simple dictionaries for the AI
    return [{"role": row["role"], "content": row["content"]} for row in rows] 


# FEEDBACK FUNCTIONS
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
    # Join feedback with messages to filter by conversation_id
    query = """
        SELECT f.user_text, f.correction, f.explanation 
        FROM feedback f
        JOIN messages m ON f.message_id = m.id
        WHERE m.conversation_id = ?
        ORDER BY f.created_at DESC
    """
    rows = cursor.execute(query, (conversation_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]