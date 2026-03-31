import os
import psycopg2
from dotenv import load_dotenv

def sync_secrets():
    # Load .env with override=True to ensure we use the project's newest keys
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path, override=True)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in .env")
        return

    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not openai_key:
        print("Error: OPENAI_API_KEY not found in .env")
        return

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Ensure settings table exists (it should, but just in case)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Update OpenAI key
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("openai_api_key", openai_key)
        )
        
        # Update Gemini key if exists
        if gemini_key:
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                ("gemini_api_key", gemini_key)
            )
            
        conn.commit()
        print(f"Successfully synchronized secrets to database.")
        print(f"OpenAI Key (masked): {openai_key[:8]}...{openai_key[-4:]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    sync_secrets()
