from fastapi import APIRouter, HTTPException, Depends
from routers.auth import get_current_user
from pydantic import BaseModel
import os
from openai import AsyncOpenAI
from rag_utils import search_teacher_notes, format_teacher_notes
from prompts import get_tutor_system_prompt
import config
from usage_utils import check_and_increment_usage

router = APIRouter(prefix="/api/tutor", tags=["tutor"])

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o"

@router.post("/chat")
async def tutor_chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    # Standard Plan Limit: 4 rounds total per day
    check_and_increment_usage(current_user["id"], current_user.get("plan_type", "standard"))

    # 1. Search for relevant teacher notes (RAG)
    context_chunks = search_teacher_notes(req.message)
    context_str = format_teacher_notes(context_chunks)
    
    # 2. Get the specific system prompt for the tutor
    system_prompt = get_tutor_system_prompt()
    if context_str:
        system_prompt += f"\n\n### 【Aki先生の指導メソッド（RAG資料）】\n{context_str}"

    # 3. LLM Call
    from google import genai
    import config
    cfg = config.get_config()
    openai_key = cfg.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    gemini_key = cfg.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    
    use_gemini = req.model.startswith("gemini") and gemini_key
    
    if use_gemini:
        try:
            client_g = genai.Client(api_key=gemini_key)
            print(f"Sending request to Gemini ({req.model}) for Tutor Chat...")
            response = client_g.models.generate_content(
                model=req.model,
                contents=req.message,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.4
                }
            )
            return {"reply": response.text}
        except Exception as e:
            error_str = str(e)
            if ("429" in error_str or "quota" in error_str.lower()) and openai_key:
                print(f"Gemini Quota Exceeded in Tutor. Falling back to GPT-4o...")
                client_oa = AsyncOpenAI(api_key=openai_key)
                response = await client_oa.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt + "\n(Note: Gemini quota exceeded, falling back to GPT-4o)"},
                        {"role": "user", "content": req.message}
                    ],
                    temperature=0.4
                )
                return {"reply": response.choices[0].message.content}
            else:
                import traceback
                print(f"Tutor Chat Error: {str(e)}")
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail=str(e))
    else:
        if not openai_key:
            raise HTTPException(status_code=503, detail="OpenAI API key not configured")
        try:
            client_oa = AsyncOpenAI(api_key=openai_key)
            response = await client_oa.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": req.message}
                ],
                temperature=0.4
            )
            return {"reply": response.choices[0].message.content}
        except Exception as e:
            import traceback
            print(f"Tutor Chat Error (OpenAI): {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
