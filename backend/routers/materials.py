from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from routers.auth import get_current_user
from pydantic import BaseModel
import httpx
import os
import random
import urllib.parse
from openai import AsyncOpenAI
import json

from prompts import get_generation_prompt
import config

router = APIRouter(prefix="/api/materials", tags=["materials"])

OLLAMA_URL = "http://localhost:11434/api/generate"

# Config 
def get_openai_client():
    key = config.get_config()["openai_api_key"]
    return AsyncOpenAI(api_key=key) if key else None

class MaterialRequest(BaseModel):
    category: str
    level: str
    topic: str
    model: str
    reference_text: str = ""

class ImageRequest(BaseModel):
    prompt: str
    model: str = "gpt-4o" # or ollama model

@router.post("/generate")
async def generate_material(req: MaterialRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="Standardプランではティーチャーツールは利用できません。Proプランへアップグレードしてください。")
    prompt = get_generation_prompt(req.category, req.level, req.topic, req.reference_text)
    
    # Model validation
    target_model = req.model
    if target_model not in ["gpt-4o", "gemini-2.0-flash"]:
        target_model = "gpt-4o"

    # OpenAI Logic
    if target_model.startswith("gpt-"):
        client = get_openai_client()
        if not client:
             raise HTTPException(status_code=503, detail="OpenAI API key not configured")
        
        try:
            response = await client.chat.completions.create(
                model=req.model,
                messages=[
                    {"role": "system", "content": "あなたは日本語教師です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return {"result": response.choices[0].message.content}
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Gemini Logic
    elif req.model.startswith("gemini"):
        # Import genai lazily or at top level (already imported commonly in main, but need here)
        import google.generativeai as genai
        
        gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
        if not gemini_key:
             raise HTTPException(status_code=503, detail="Gemini API key not configured")
        
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(target_model)
            
            # Use 'response_mime_type' only if we wanted JSON, but here we generally want text.
            # However, if the prompt asks for JSON (like Quiz), we might get JSON text.
            # We'll just return whatever Gemini gives as string.
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.2} 
            )
            # Check for safety blocking
            if response.prompt_feedback.block_reason:
                raise HTTPException(status_code=400, detail=f"Blocked by Gemini Safety Filter: {response.prompt_feedback}")
            
            try:
                return {"result": response.text}
            except ValueError:
                 # If response.text fails, it's likely empty due to safety or other reason
                 print(f"Gemini Empty Response: {response.prompt_feedback}")
                 raise HTTPException(status_code=500, detail="Gemini returned no text (likely safety filter).")
        except Exception as e:
            print(f"Gemini Material Error: {e}")
            raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")

    # Model Restriction strictly enforced above
    else:
        raise HTTPException(status_code=400, detail="Unsupported model")


@router.post("/image")
async def generate_image(req: ImageRequest, current_user: dict = Depends(get_current_user)):
    if current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="Standardプランでは画像生成機能は利用できません。")
    # STEP 1: Translate/Expand Prompt using LLM (Ollama or OpenAI)
    translation_prompt = f"""
    Convert the following Japanese topic into a list of 5-8 descriptive English keywords for image generation.
    Focus on visual elements, style, and atmosphere.
    Response should be ONLY the keywords separated by commas.
    
    Topic: {req.prompt}
    Keywords (English):"""
    
    keywords = ""
    try:
        client = get_openai_client()
        if req.model.startswith("gpt-") and client:
             response = await client.chat.completions.create(
                model=req.model,
                messages=[{"role": "user", "content": translation_prompt}],
                max_tokens=100
             )
             keywords = response.choices[0].message.content.strip()
        else:
             # Default to Ollama if OpenAI not strict or not avail
             model_to_use = req.model if not req.model.startswith("gpt-") else "llama3.1:latest" # Fallback if OpenAI key missing but requested?
             # Safer: just use what is requested unless it's cloud and key is missing, then fallback to something generic or fail. 
             # Let's assume user passes a valid local model or valid openai logic.
             
             payload = {
                "model": model_to_use,
                "prompt": translation_prompt,
                "stream": False
            }
             async with httpx.AsyncClient() as client:
                response = await client.post(OLLAMA_URL, json=payload, timeout=20.0)
                if response.status_code == 200:
                    keywords = response.json().get("response", "").strip()
    
        # Cleanup
        keywords = "".join(c for c in keywords if c.isalnum() or c in " ,-")
        if not keywords: keywords = req.prompt # Fallback

    except Exception as e:
        print(f"Translation failed: {e}")
        keywords = req.prompt 

    # STEP 2: Pollinations AI URL
    style_modifiers = "clean flat illustration, minimal textbook style, soft colors, white background"
    full_prompt = f"{keywords}, {style_modifiers}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    seed = random.randint(1000, 999999)
    
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&seed={seed}&nologo=true"
    
    return {"image_url": image_url}

@router.post("/upload-reference")
async def upload_reference(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="Standardプランではファイルアップロード機能は利用できません。")
    filename = file.filename.lower()
    content = await file.read()
    
    try:
        from utils import extract_text_from_pptx, extract_text_from_xlsx
        if filename.endswith(".pptx"):
            text = extract_text_from_pptx(content)
        elif filename.endswith(".xlsx"):
            text = extract_text_from_xlsx(content)
        else:
            raise HTTPException(status_code=400, detail="Only .pptx and .xlsx files are supported.")
        
        return {"filename": file.filename, "extracted_text": text}
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
