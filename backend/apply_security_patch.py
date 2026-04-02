import psycopg2
import os
from dotenv import load_dotenv

# Load database connection
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

sql_script = """
-- 1. Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_embeddings ENABLE ROW LEVEL SECURITY;

-- 2. Clean up existing policies if any (to avoid "already exists" errors)
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Users can view their own transactions" ON transactions;
DROP POLICY IF EXISTS "Users can view their own reset tokens" ON password_reset_tokens;
DROP POLICY IF EXISTS "Students can read teacher notes" ON teacher_embeddings;

-- 3. Create Security Policies
-- USERS
CREATE POLICY "Users can view their own profile" ON users FOR SELECT USING (id = auth.uid()::text);
CREATE POLICY "Users can update their own profile" ON users FOR UPDATE USING (id = auth.uid()::text) WITH CHECK (id = auth.uid()::text);

-- TRANSACTIONS
CREATE POLICY "Users can view their own transactions" ON transactions FOR SELECT USING (user_id = auth.uid()::text);

-- RESET TOKENS
CREATE POLICY "Users can view their own reset tokens" ON password_reset_tokens FOR SELECT USING (user_id = auth.uid()::text);

-- TEACHER NOTES (Public Read for Authenticated)
CREATE POLICY "Students can read teacher notes" ON teacher_embeddings FOR SELECT TO authenticated USING (true);
"""

def apply_patch():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🚀 Applying security patches to Supabase...")
        cur.execute(sql_script)
        print("✅ Security RLS and Policies applied successfully!")
        
        # Verify RLS Status
        cur.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('users', 'transactions', 'password_reset_tokens', 'settings', 'teacher_embeddings');
        """)
        results = cur.fetchall()
        print("\n--- Current RLS Status ---")
        for table, rls in results:
            status = "ENABLED" if rls else "DISABLED"
            print(f"- {table}: {status}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to apply security patch: {e}")

if __name__ == "__main__":
    apply_patch()
