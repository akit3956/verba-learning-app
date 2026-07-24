import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        c.execute("SELECT id, email, username, created_at FROM users ORDER BY created_at DESC")
        users = c.fetchall()

        print(f"\n{'='*60}")
        print(f" TOTAL REGISTERED ACCOUNTS: {len(users)}")
        print(f"{'='*60}")
        print(f"{'Username':<20} | {'Email':<30}")
        print("-" * 60)

        for user in users:
            email_display = user['email'] if user['email'] else "N/A"
            username_display = user['username'] if user['username'] else "N/A"
            print(f"{username_display:<20} | {email_display:<30}")
            
        print(f"{'='*60}\n")
        
        c.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()
