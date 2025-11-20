import sqlite3
import json
from pathlib import Path
from datetime import datetime 
from typing import List, Optional, Dict

# Define the database file location
DB_FILE = Path.cwd() / "rod.db"

def get_connection():
    """ Establishes a connection to the SQLite database. """
    conn = sqlite3.connect(DB_FILE)
    # Make the rows behave like dicts
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """ Initializes the databse tables. """
    conn = get_connection()
    cursor = conn.cursor()

    # Creates users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        created_at TEXT
    )
    """)

    # Creates conversations table
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

def get_conversation_context(conversation_id: int) -> Optional[dict]:
    """Retrieves the media context (if any) for a specific thread."""
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT context_lock FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
    conn.close()
    
    if row and row['context_lock']:
        return json.loads(row['context_lock'])
    return None

# MESSAGE FUNCTIONS
def add_message(conversation_id: int, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

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

def get_user_conversations(user_id: str) -> List[Dict]:
    """
    Returns a summary list of all conversations for the burger menu.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # We join with messages to get a snippet of the first message (the "Title")
    # This query gets the conversation ID, the date, and the first user message as the 'title'
    query = """
        SELECT c.id, c.created_at, 
               (SELECT content FROM messages m WHERE m.conversation_id = c.id AND m.role = 'user' LIMIT 1) as title
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
            "title": row["title"] or "New Conversation"
        } 
        for row in rows
    ]