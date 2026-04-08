from fastapi import HTTPException
from database import get_db_connection
from datetime import date

def check_and_increment_usage(user_id: str, plan_type: str, limit: int = 4):
    """
    Checks if a user has exceeded their daily limit and increments the count.
    Only applies to 'standard' users.
    """
    if plan_type != "standard":
        return True # Unlimited for Pro/Founder
    
    conn = get_db_connection()
    c = conn.cursor()
    today = date.today()
    
    try:
        # Get or create today's usage record
        c.execute("""
            INSERT INTO daily_usage (user_id, usage_date, total_count)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, usage_date)
            DO UPDATE SET total_count = daily_usage.total_count + 1
            RETURNING total_count
        """, (user_id, today))
        
        new_count = c.fetchone()[0]
        
        if new_count > limit:
            # We already incremented, but since we are blocking, 
            # we don't strictly need to roll back for such a small counter, 
            # but if we want to be precise, we could.
            conn.commit()
            raise HTTPException(
                status_code=403, 
                detail=f"本日の無料利用枠（{limit}回）を超えました。Proプランにアップグレードして無制限に学びましょう！"
            )
        
        conn.commit()
        return True
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Usage tracking error: {e}")
        return True # Fail open for user experience, but log error
    finally:
        c.close()
        conn.close()
