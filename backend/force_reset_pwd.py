import psycopg2
import psycopg2.extras
import os
import bcrypt
from dotenv import load_dotenv

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        c = conn.cursor()
        
        # New temporary password
        new_password = "password123"
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
        
        c.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_password, 'aki@example.com'))
        conn.commit()
        
        if c.rowcount > 0:
            print(f"Successfully reset password for aki@example.com to: {new_password}")
        else:
            print("User not found!")
            
        c.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()
