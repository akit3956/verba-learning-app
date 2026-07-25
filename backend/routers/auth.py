from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
import uuid
import psycopg2
import psycopg2.extras
import secrets
import hashlib
import requests
import base64

# Re-use from database.py
from database import get_db_connection
from usage_utils import get_usage_count

# Settings for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days for beta convenience

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    address: str
    password: str
    is_founder: bool = False
    plan_type: str = "standard"
    paypal_subscription_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    plan_type: str = "standard"
    created_at: Optional[datetime] = None

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class AdminUserResponse(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Verify session is still active
    if jti:
        c.execute("SELECT 1 FROM user_sessions WHERE jti = %s", (jti,))
        if not c.fetchone():
            c.close()
            conn.close()
            raise credentials_exception

    c.execute("SELECT * FROM users WHERE email = %s", (username,))
    user = c.fetchone()
    c.close()
    conn.close()
    
    if user is None:
        raise credentials_exception
    return dict(user)

@router.post("/register", response_model=Token)
async def register(user: UserCreate, request: Request):
    try:
        conn = get_db_connection()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="データベースに接続できません。少し時間を置いてから再試行してください。"
        )

    try:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Check if email exists
        c.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if c.fetchone():
            c.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
            
        client_ip = request.client.host if request.client else "0.0.0.0"
        
        # Anti-Multi-Account: Max 2 accounts per IP
        c.execute("SELECT COUNT(*) FROM users WHERE registration_ip = %s", (client_ip,))
        ip_count = c.fetchone()[0]
        if ip_count >= 2:
            c.close()
            conn.close()
            raise HTTPException(status_code=400, detail="同じ端末（IP）から登録できるアカウント数の上限に達しました。")

        # Founder's Cap: Max 100 users
        plan_type = "founder" if user.is_founder else user.plan_type
        if plan_type == "founder":
            c.execute("SELECT COUNT(*) FROM users WHERE plan_type = 'founder'")
            founder_count = c.fetchone()[0]
            if founder_count >= 100:
                c.close()
                conn.close()
                raise HTTPException(status_code=403, detail="Founder's Passは完売いたしました。StandardまたはProプランをご利用ください。")

        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)

        c.execute("INSERT INTO users (id, email, username, full_name, address, password_hash, plan_type, registration_ip, paypal_subscription_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  (user_id, user.email, user.username, user.full_name, user.address, hashed_password, plan_type, client_ip, user.paypal_subscription_id))
        
        # Log subscription
        if user.paypal_subscription_id:
            print(f"New User {user.email} registered with Subscription: {user.paypal_subscription_id}")

        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration Error: {e}")
        raise HTTPException(status_code=500, detail="登録処理に失敗しました。データベースの状態を確認してください。")
    finally:
        c.close()
        conn.close()
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        conn = get_db_connection()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="データベースに接続できません。しばらくしてからもう一度お試しください。"
        )

    try:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
        user = c.fetchone()
        c.close()
        conn.close()
    except Exception as e:
        print(f"Login Error: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail="ログイン処理中にエラーが発生しました。")
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # --- Multi-device handling ---
    jti = str(uuid.uuid4())
    client_ip = request.client.host if request.client else "0.0.0.0"
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO user_sessions (user_id, jti, ip_address) VALUES (%s, %s, %s)", (user["id"], jti, client_ip))
        
        # Keep only max 2 sessions per user
        c.execute("""
            DELETE FROM user_sessions 
            WHERE user_id = %s AND id NOT IN (
                SELECT id FROM user_sessions 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 2
            )
        """, (user["id"], user["id"]))
        conn.commit()
        c.close()
        conn.close()
    except Exception as e:
        print(f"Session Error: {e}")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "jti": jti}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user.get("email"),
        plan_type=current_user.get("plan_type", "standard"),
        created_at=current_user.get("created_at")
    )

@router.get("/usage")
async def get_user_usage(current_user: dict = Depends(get_current_user)):
    count = get_usage_count(current_user["id"])
    return {
        "count": count,
        "limit": 4, # Standard limit
        "plan_type": current_user.get("plan_type", "standard")
    }

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if user exists
    c.execute("SELECT id FROM users WHERE email = %s", (request.email,))
    user = c.fetchone()
    
    if user:
        # Generate token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        c.execute("""
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
        """, (user['id'], token_hash, expires_at))
        conn.commit()
        
        # Simulate sending email
        print(f"\n[SIMULATED EMAIL] Password reset request for {request.email}")
        print(f"Reset Token: {token}\n")
        
    c.close()
    conn.close()
    
    # Always return a generic success message to prevent email enumeration
    return {"message": "If that email is registered, a password reset link has been generated (check terminal for token)."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    token_hash = hashlib.sha256(request.token.encode('utf-8')).hexdigest()
    
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Find active token
    c.execute("""
        SELECT * FROM password_reset_tokens 
        WHERE token_hash = %s AND used = FALSE AND expires_at > %s
    """, (token_hash, datetime.utcnow()))
    reset_record = c.fetchone()
    
    if not reset_record:
        c.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    # Update user password
    hashed_password = get_password_hash(request.new_password)
    try:
        c.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, reset_record['user_id']))
        c.execute("UPDATE password_reset_tokens SET used = TRUE WHERE id = %s", (reset_record['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        c.close()
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to reset password")
        
    c.close()
    conn.close()
    
    return {"message": "Password has been successfully reset."}

@router.get("/users", response_model=list[AdminUserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    # Simple Admin Check: Ensure this is Aki's account
    if current_user.get("email") != "aki@example.com" and current_user.get("username") != "Aki":
        raise HTTPException(status_code=403, detail="Forbidden, admin only branch")
        
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    c.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
    users = c.fetchall()

    c.close()
    conn.close()

    return [
        AdminUserResponse(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            created_at=u["created_at"]
        ) for u in users
    ]

from fastapi.responses import StreamingResponse
import io
import csv

@router.get("/users/export")
async def export_users_csv(current_user: dict = Depends(get_current_user)):
    if current_user.get("email") != "aki@example.com" and current_user.get("username") != "Aki":
        raise HTTPException(status_code=403, detail="Forbidden, admin only branch")
        
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get users and their active sessions
    c.execute("""
        SELECT u.id, u.username, u.email, u.plan_type, u.created_at, 
               string_agg(s.ip_address, ', ') as active_ips
        FROM users u
        LEFT JOIN user_sessions s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    rows = c.fetchall()
    c.close()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Username", "Email", "Plan", "Created At", "Active IPs"])
    for row in rows:
        writer.writerow([row['id'], row['username'], row['email'], row['plan_type'], row['created_at'], row['active_ips'] or "None"])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=verba_users_export.csv"}
    )


class UpgradePlanRequest(BaseModel):
    paypal_order_id: str
    paypal_subscription_id: Optional[str] = None
    plan_type: str

@router.post("/upgrade-plan")
async def upgrade_plan(req: UpgradePlanRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    if req.plan_type not in ["pro", "founder"]:
        raise HTTPException(status_code=400, detail="Invalid plan type requested for upgrade.")

    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    c.execute("""
        UPDATE users
        SET plan_type = %s, paypal_subscription_id = %s
        WHERE id = %s
        RETURNING plan_type, paypal_subscription_id
    """, (req.plan_type, req.paypal_subscription_id, user_id))
    updated_user = c.fetchone()

    if req.paypal_subscription_id:
        print(f"User {user_id} upgraded to {req.plan_type} with Subscription: {req.paypal_subscription_id}")
    else:
        print(f"User {user_id} upgraded to {req.plan_type} with Order: {req.paypal_order_id}")

    if not updated_user:
        conn.rollback()
        c.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found for plan upgrade.")

    conn.commit()
    c.close()
    conn.close()

    return {"status": "success", "new_plan": updated_user["plan_type"]}


def cancel_paypal_subscription(subscription_id: str):
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET_KEY")
    # Default to sandbox if env is not explicitly set to production
    # api_url = "https://api-m.paypal.com" if os.getenv("ENV") == "production" else "https://api-m.sandbox.paypal.com"
    # For now, let's use production URL since the app seems to be live
    api_url = "https://api-m.paypal.com"
    
    if not client_id or not secret:
        print("PayPal credentials not set. Skipping cancellation.")
        return False
        
    try:
        auth_string = f"{client_id}:{secret}"
        base64_auth = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        token_res = requests.post(
            f"{api_url}/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {base64_auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        if not token_res.ok:
            print("Failed to get PayPal token:", token_res.text)
            return False
            
        access_token = token_res.json()["access_token"]
        
        cancel_res = requests.post(
            f"{api_url}/v1/billing/subscriptions/{subscription_id}/cancel",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json={"reason": "User deleted account in Verba App"}
        )
        if cancel_res.ok or cancel_res.status_code == 204:
            print(f"Successfully cancelled PayPal subscription {subscription_id}")
            return True
        else:
            print(f"Failed to cancel subscription {subscription_id}: {cancel_res.text}")
            return False
    except Exception as e:
        print(f"PayPal API Error: {e}")
        return False

@router.delete("/me")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    user_id = current_user["id"]
    try:
        # Cancel PayPal subscription if exists
        c.execute("SELECT paypal_subscription_id FROM users WHERE id = %s", (user_id,))
        row = c.fetchone()
        sub_id = row[0] if row else None
        
        if sub_id:
            cancel_paypal_subscription(sub_id)
            
        c.execute("DELETE FROM user_sessions WHERE user_id = %s", (user_id,))
        c.execute("DELETE FROM password_reset_tokens WHERE user_id = %s", (user_id,))
        c.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
        c.execute("DELETE FROM daily_usage WHERE user_id = %s", (user_id,))
        c.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Account Deletion Error: {e}")
        raise HTTPException(status_code=500, detail="アカウントの削除に失敗しました。")
    finally:
        c.close()
        conn.close()
        
    return {"message": "Account successfully deleted"}
