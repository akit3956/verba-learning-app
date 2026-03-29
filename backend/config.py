import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_db_connection():
    import psycopg2
    DB_URL = os.getenv("DATABASE_URL")
    if not DB_URL:
        return None
    return psycopg2.connect(DB_URL)

def load_config():
    # Initial defaults from ENV
    config_dict = {
        "model": os.getenv("DEFAULT_MODEL", "gemma2"),
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "gemini_api_key": os.getenv("GEMINI_API_KEY", "")
    }
    
    conn = get_db_connection()
    if not conn:
        return config_dict
        
    try:
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall()
        for key, value in rows:
            if key in config_dict:
                config_dict[key] = value
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error loading config from DB: {e}")
        
    return config_dict

# In-memory cache for performance
global_config = load_config()

def get_config():
    return load_config()

def update_config(key, value):
    global_config[key] = value
    
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        cur = conn.cursor()
        # Wait, PostgreSQL syntax for REPLACE is different.
        cur.execute("""
            INSERT INTO settings (key, value) 
            VALUES (%s, %s) 
            ON CONFLICT (key) 
            DO UPDATE SET value = EXCLUDED.value
        """, (key, value))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error saving config to DB: {e}")
