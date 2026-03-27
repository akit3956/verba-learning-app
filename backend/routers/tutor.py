from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user
from pydantic import BaseModel
import os
from openai import AsyncOpenAI
from rag_utils import search_teacher_notes, format_teacher_notes
from prompts import get_tutor_system_prompt
import config

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o"

@router.post("/chat")
async def tutor_chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    # Block feature for standard users
    if current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="StandardプランではAIチューター機能は利用できません。Proプラン以上へアップグレードしてください。")

    # 1. Search for relevant teacher notes (RAG)
    context_chunks = search_teacher_notes(req.message)
    context_str = format_teacher_notes(context_chunks)
    
    # 2. Get the specific system prompt for the tutor
    system_prompt = get_tutor_system_prompt()
    if context_str:
        system_prompt += f"\n\n{context_str}"
    
    # 3. LLM Call
    api_key = os.getenv("OPENAI_API_KEY") or config.get_config().get("openai_api_key")
    if not api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
        
    client = AsyncOpenAI(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            model=req.model if req.model in ["gpt-4o", "gemini-2.0-flash"] else "gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.4
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"Tutor Chat Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Tutor Error: {str(e)}")
