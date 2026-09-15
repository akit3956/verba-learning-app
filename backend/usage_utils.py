from fastapi import HTTPException
from database import get_db_connection
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))

# A-0b: 月次利用上限（Free 20 / 有料 500）。リセットはJST基準で毎月1日。
# founderはあえてキーを設けず上限なしのまま（Vee企画審査で維持方針を確認済み）。
PLAN_MONTHLY_LIMITS = {
    "standard": 20,  # Free
    "pro": 500,      # 有料（$6.99/月）
}


def _today_jst() -> date:
    return datetime.now(JST).date()


def get_monthly_limit(plan_type: str):
    """月次上限を返す。キーに無いプラン（founder等）はNone＝上限なし。"""
    return PLAN_MONTHLY_LIMITS.get(plan_type)


def check_and_increment_usage(user_id: str, plan_type: str):
    """
    当月（JST基準）の利用回数をチェックし、カウントを増やす。
    plan_typeに月次上限が設定されていない場合（founder等）は無制限。
    """
    limit = get_monthly_limit(plan_type)
    if limit is None:
        return True  # 上限なし

    conn = get_db_connection()
    if not conn:
        print("Warning: Skipping usage tracking because database is unreachable.")
        return True # Fail open

    c = conn.cursor()
    today = _today_jst()

    try:
        # 日次テーブルはそのまま流用し、今日分をインクリメント
        c.execute("""
            INSERT INTO daily_usage (user_id, usage_date, total_count)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id, usage_date)
            DO UPDATE SET total_count = daily_usage.total_count + 1
        """, (user_id, today))

        # 当月合計（JST基準の月初〜今日）を集計して判定
        c.execute("""
            SELECT COALESCE(SUM(total_count), 0) FROM daily_usage
            WHERE user_id = %s
              AND DATE_TRUNC('month', usage_date) = DATE_TRUNC('month', %s::date)
        """, (user_id, today))
        month_count = c.fetchone()[0]

        if month_count > limit:
            conn.commit()
            raise HTTPException(
                status_code=403,
                detail=f"今月の利用枠（{limit}回）を超えました。プランをアップグレードしてもっと学びましょう！"
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

def get_usage_count(user_id: str):
    """当月（JST基準）の利用回数合計を返す。"""
    conn = get_db_connection()
    if not conn:
        return 0
    c = conn.cursor()
    today = _today_jst()
    try:
        c.execute("""
            SELECT COALESCE(SUM(total_count), 0) FROM daily_usage
            WHERE user_id = %s
              AND DATE_TRUNC('month', usage_date) = DATE_TRUNC('month', %s::date)
        """, (user_id, today))
        row = c.fetchone()
        return row[0] if row else 0
    except Exception:
        return 0
    finally:
        c.close()
        conn.close()
