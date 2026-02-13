from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_db_connection, UserBalance, Transaction

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

class RewardRequest(BaseModel):
    user_id: str
    amount: int
    description: str

class SpendRequest(BaseModel):
    user_id: str
    amount: int
    description: str

@router.get("/balance/{user_id}", response_model=UserBalance)
async def get_balance(user_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserBalance(
        user_id=user["id"],
        username=user["username"],
        balance=user["edu_balance"]
    )

@router.get("/transactions/{user_id}")
async def get_transactions(user_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    transactions = []
    for row in rows:
        transactions.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "amount": row["amount"],
            "type": row["type"],
            "description": row["description"],
            "timestamp": row["timestamp"]
        })
    return transactions

@router.post("/reward")
async def add_reward(req: RewardRequest):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check user
    c.execute("SELECT edu_balance FROM users WHERE id = ?", (req.user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    new_balance = user["edu_balance"] + req.amount
    
    # Update balance
    c.execute("UPDATE users SET edu_balance = ? WHERE id = ?", (new_balance, req.user_id))
    
    # Log transaction
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
              (req.user_id, req.amount, 'reward', req.description))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "new_balance": new_balance}

@router.post("/spend")
async def spend_tokens(req: SpendRequest):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check user
    c.execute("SELECT edu_balance FROM users WHERE id = ?", (req.user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["edu_balance"] < req.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    new_balance = user["edu_balance"] - req.amount
    
    # Update balance
    c.execute("UPDATE users SET edu_balance = ? WHERE id = ?", (new_balance, req.user_id))
    
    # Log transaction
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
              (req.user_id, req.amount, 'spend', req.description))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "new_balance": new_balance}

class TransferRequest(BaseModel):
    sender_id: str
    receiver_id: str
    amount: int
    description: str = "Transfer"

@router.post("/transfer")
async def transfer_tokens(req: TransferRequest):
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Check Sender
    c.execute("SELECT edu_balance FROM users WHERE id = ?", (req.sender_id,))
    sender = c.fetchone()
    if not sender:
        conn.close()
        raise HTTPException(status_code=404, detail="Sender not found")
    
    if sender["edu_balance"] < req.amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 2. Check Receiver
    # For simulation, if receiver doesn't exist, we could auto-create or fail.
    # Let's fail if not found to be safe, or just allow transfer to any ID for simulation.
    # To be realistic, let's check.
    c.execute("SELECT edu_balance FROM users WHERE id = ?", (req.receiver_id,))
    receiver = c.fetchone()
    if not receiver:
        # If receiver doesn't exist, Create them? Or fail?
        # For this "Mock" wallet, let's Auto-Create if missing to make testing easier.
        c.execute("INSERT INTO users (id, username, edu_balance) VALUES (?, ?, ?)", (req.receiver_id, f"User {req.receiver_id}", 0))
        receiver = {"edu_balance": 0}
    
    # 3. Perform Transfer
    new_sender_bal = sender["edu_balance"] - req.amount
    new_receiver_bal = receiver["edu_balance"] + req.amount
    
    c.execute("UPDATE users SET edu_balance = ? WHERE id = ?", (new_sender_bal, req.sender_id))
    c.execute("UPDATE users SET edu_balance = ? WHERE id = ?", (new_receiver_bal, req.receiver_id))
    
    # 4. Log Transactions (Both sides)
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
              (req.sender_id, req.amount, 'transfer_out', f"To {req.receiver_id}: {req.description}"))
    
    c.execute("INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
              (req.receiver_id, req.amount, 'transfer_in', f"From {req.sender_id}: {req.description}"))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success", 
        "sender_new_balance": new_sender_bal,
        "receiver_new_balance": new_receiver_bal
    }
