import sqlite3
import os
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

DB_PATH = "jlpt.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # User Table (Keep it simple, maybe just a single user for now or simple ID)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT,
            edu_balance INTEGER DEFAULT 0
        )
    ''')
    
    # Transaction History
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            amount INTEGER,
            type TEXT, -- 'reward', 'spend'
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Seed default user if not exists
    c.execute("SELECT * FROM users WHERE id = 'user_1'")
    if not c.fetchone():
        c.execute("INSERT INTO users (id, username, edu_balance) VALUES (?, ?, ?)", 
                  ('user_1', 'Akira', 100)) # Start with 100 VERBA
        
    conn.commit()
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
