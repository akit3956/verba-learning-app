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

# Re-use from database.py
from database import get_db_connection

# Settings for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days for beta convenience

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    is_founder: bool = False
    plan_type: str = "standard"

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    username: str
    vrb_balance: int
    plan_type: str = "standard"

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class AdminUserResponse(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    vrb_balance: int
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
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM users WHERE email = %s", (username,))
    user = c.fetchone()
    c.close()
    conn.close()
    
    if user is None:
        raise credentials_exception
    return dict(user)

@router.post("/register", response_model=Token)
async def register(user: UserCreate, request: Request):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check if username exists
    c.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing = c.fetchone()
    if existing:
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
    initial_bonus = 10000 if plan_type == 'founder' else 0
    
    try:
        c.execute("INSERT INTO users (id, email, username, password_hash, vrb_balance, plan_type, registration_ip) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (user_id, user.email, user.username, hashed_password, initial_bonus, plan_type, client_ip))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        c.close()
        conn.close()
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT * FROM users WHERE email = %s", (form_data.username,))
    user = c.fetchone()
    c.close()
    conn.close()
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        vrb_balance=current_user["vrb_balance"],
        plan_type=current_user.get("plan_type", "standard")
    )

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
    
    c.execute("SELECT id, username, email, vrb_balance, created_at FROM users ORDER BY created_at DESC")
    users = c.fetchall()
    
    c.close()
    conn.close()
    
    return [
        AdminUserResponse(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            vrb_balance=u["vrb_balance"] if u["vrb_balance"] is not None else 0,
            created_at=u["created_at"]
        ) for u in users
    ]
