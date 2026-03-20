import psycopg2
import psycopg2.extras
import os
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv

import bcrypt

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DB_URL:
        raise ValueError("DATABASE_URL is not set in .env")
    conn = psycopg2.connect(DB_URL)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # User Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT,
            password_hash TEXT,
            vrb_balance INTEGER DEFAULT 0,
            nationality TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transaction History
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            amount INTEGER,
            type TEXT, -- 'reward', 'spend'
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Password Reset Tokens
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            token_hash TEXT,
            expires_at TIMESTAMP,
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if password_hash column exists (Migration)
    c.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users';
    """)
    columns = [row[0] for row in c.fetchall()]
    
    if "password_hash" not in columns:
        try:
            c.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            fallback_hash = bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8")
            c.execute("UPDATE users SET password_hash = %s WHERE password_hash IS NULL", (fallback_hash,))
        except Exception:
            conn.rollback()
            pass # ignore if schema is already updated

    # Check if email exists (Migration)
    if "email" not in columns:
        try:
            c.execute("ALTER TABLE users ADD COLUMN email TEXT")
            c.execute("UPDATE users SET email = username || '@example.com' WHERE email IS NULL")
        except Exception:
            conn.rollback()
            pass
            
    # Check if nationality exists (From LP integration)
    if "nationality" not in columns:
        try:
            c.execute("ALTER TABLE users ADD COLUMN nationality TEXT")
        except Exception:
            conn.rollback()
            pass
            
    # Check if created_at exists (From LP integration)
    if "created_at" not in columns:
        try:
            c.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except Exception:
            conn.rollback()
            pass
        
    # Seed default user if not exists
    c.execute("SELECT * FROM users WHERE id = 'user_1'")
    if not c.fetchone():
        seed_hash = bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8")
        c.execute("INSERT INTO users (id, email, username, password_hash, vrb_balance) VALUES (%s, %s, %s, %s, %s)", 
                  ('user_1', 'aki@example.com', 'Aki', seed_hash, 100)) # Start with 100 VERBA
        
    conn.commit()
    c.close()
    conn.close()

# Pydantic Models for DB interactions
class Transaction(BaseModel):
    id: int
    user_id: str
    amount: int
    type: str
    description: str
    timestamp: str

class UserBalance(BaseModel):
    user_id: str
    username: str
    balance: int
