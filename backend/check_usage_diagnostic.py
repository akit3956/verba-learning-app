import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import database
    from usage_utils import check_and_increment_usage, get_usage_count

    # Try to init_db so table is guaranteed created
    database.init_db()
    print("Database initialized successfully.")
    
    # Get a user (any standard user)
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE plan_type = 'standard' LIMIT 1")
    row = c.fetchone()
    
    if not row:
        print("No standard user found. Creating a dummy one.")
        user_id = "test_standard_user_123"
        c.execute("INSERT INTO users (id, plan_type) VALUES (%s, 'standard') ON CONFLICT DO NOTHING", (user_id,))
        conn.commit()
    else:
        user_id = row[0]
        print(f"Testing with user_id: {user_id}")

    # Check current count
    count = get_usage_count(user_id)
    print(f"Current count: {count}")
    
    # Increment
    print("Incrementing...")
    check_and_increment_usage(user_id, "standard")
    
    # Check current count again
    new_count = get_usage_count(user_id)
    print(f"New count: {new_count}")

except Exception as e:
    import traceback
    traceback.print_exc()

