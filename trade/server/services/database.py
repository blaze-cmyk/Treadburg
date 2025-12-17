"""
Simple database service for user management
Replace with your preferred database (PostgreSQL, MongoDB, etc.)
"""
import sqlite3
import os
from pathlib import Path
import logging

log = logging.getLogger(__name__)

# Database file path
DB_PATH = os.getenv("DATABASE_PATH", "data/users.db")

def get_db_connection():
    """Get database connection"""
    # Create data directory if it doesn't exist
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            picture TEXT,
            credits_balance INTEGER DEFAULT 100,
            subscription_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            email_verified BOOLEAN DEFAULT 0
        )
    """)
    
    # Create sessions table (optional)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    log.info("Database initialized successfully")

# Initialize database on import
try:
    init_database()
except Exception as e:
    log.error(f"Failed to initialize database: {e}")
