from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import re
import os
import random
import urllib.parse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from openai import AsyncOpenAI
import google.generativeai as genai
from prompts import get_quiz_prompt, get_aki_style_prompt

from routers import wallet, materials, auth, tutor
from routers.auth import get_current_user
from usage_utils import check_and_increment_usage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
from pdf_utils import get_random_page_image
from pdf_context import load_context_for_level

def clean_json_string(s: str) -> str:
    """Robustly clean JSON string from LLM responses, removing markdown blocks."""
    if not s:
        return ""
    # Remove ```json ... ``` or ``` ... ```
    s = re.sub(r'^```(?:json)?\s*', '', s, flags=re.MULTILINE)
    s = re.sub(r'\s*```$', '', s, flags=re.MULTILINE)
    return s.strip()

# New Modules (Trigger Reload)
from database import init_db

class ConfigUpdate(BaseModel):
    model: str
    openai_api_key: str = ""
    gemini_api_key: str = ""

load_dotenv(override=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    print("Initializing Database...")
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    yield
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

# Include Routers
app.include_router(auth.router)
app.include_router(wallet.router)
app.include_router(materials.router)
app.include_router(tutor.router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://verba-learning-app.vercel.app",
        "https://verba-learning-app.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class GenerateRequest(BaseModel):
    category: str  # "grammar", "vocab", "reading"
    level: str     # "N5", "N4", "N3", "N2", "N1"
    topic: str = ""
    mode: str = "single" # "single", "small_test", "mock_test"
    model: str = "gpt-4o"
    include_image: bool = False 

class MockTestRequest(BaseModel):
    level: str
    model: str = "gpt-4o"
    api_key: str = ""

class InquiryRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str

def get_openai_client():
    cfg = config.get_config()
    api_key = cfg.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)

@app.get("/config")
async def get_config_endpoint():
    raw_config = config.get_config()
    # Mask keys for frontend display
    masked_config = raw_config.copy()
    for key in ["openai_api_key", "gemini_api_key"]:
        val = raw_config.get(key, "")
        if val and len(val) > 12:
            masked_config[key] = f"{val[:8]}...{val[-4:]}"
        elif val:
            masked_config[key] = "****"
    return masked_config

@app.post("/config")
async def update_config_endpoint(update: ConfigUpdate):
    # Only update if the key provided is NOT a masked version
    if update.openai_api_key and "*" not in update.openai_api_key:
        config.update_config("openai_api_key", update.openai_api_key)
        # Re-initialize OpenAI client
        # Force reload in config service (handled by config.update_config)
        pass

    if update.gemini_api_key and "*" not in update.gemini_api_key:
        config.update_config("gemini_api_key", update.gemini_api_key)
        genai.configure(api_key=update.gemini_api_key)

    if update.model:
        config.update_config("model", update.model)
    
    return {"message": "Config updated", "config": await get_config_endpoint()}

@app.get("/api/health")
async def health_check():
    from database import get_db_connection
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": f"error: {str(e)}"}



@app.get("/config/test")
async def test_api_config(current_user: dict = Depends(get_current_user)):
    if current_user.get("username") != "aki":
        raise HTTPException(status_code=403, detail="Admin only")
    
    results = {"openai": "Not Configured", "gemini": "Not Configured"}
    
    # Test OpenAI
    client = get_openai_client()
    if client:
        try:
            # Simple call to list models to verify key
            await client.models.list()
            results["openai"] = "✅ Success"
        except Exception as e:
            results["openai"] = f"❌ Error: {str(e)}"
    
    # Test Gemini
    gemini_key = config.get_config().get("gemini_api_key")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            # Simple call to list models
            genai.list_models()
            results["gemini"] = "✅ Success"
        except Exception as e:
            results["gemini"] = f"❌ Error: {str(e)}"
            
    return results

@app.get("/models")
async def get_models():
    models = [
        {"name": "gpt-4o", "type": "cloud", "size": "OpenAI (High Accuracy)"},
        {"name": "gemini-2.0-flash", "type": "cloud", "size": "Google (Fast & Accurate)"}
    ]
    return {"models": models}

import rag_utils # Import the RAG module

@app.post("/generate")
async def generate_quiz(req: GenerateRequest, current_user: dict = Depends(get_current_user)):
    # Standard Plan Limit: 4 rounds total per day (合算)
    check_and_increment_usage(current_user["id"], current_user.get("plan_type", "standard"))

    # Block advanced features for standard users
    # Block advanced features for standard users
    if req.mode in ["mock_test", "all_items"] and current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="Standardプランではこの機能は利用できません。Proプラン以上へアップグレードしてください。")
    # Determine count based on mode
    count = 1
    if req.mode == "small_test":
        count = 5
    elif req.mode == "mock_test":
        count = 10 

    # Look for reference file (Keep for Reading context)
    reference_text = ""
    ref_path = f"references/{req.level}_{req.category}.txt"
    if os.path.exists(ref_path):
        try:
            with open(ref_path, "r", encoding="utf-8") as f:
                reference_text = f.read()
        except Exception as e:
            print(f"Failed to load reference: {e}")

    # 1. Load context from N5~N1PDF files (PDF, PPTX, XLSX)
    try:
        from pdf_context import load_context_for_level
        pdf_ctx = load_context_for_level(req.level, req.category)
        if pdf_ctx:
            reference_text += f"\n\n【提供された教材資料】\n{pdf_ctx}"
    except Exception as e:
        print(f"Error loading PDF/PPT context from folder: {e}")

    # --- Load Teacher Notes (Vector RAG) and Grammar DB ---
    try:
        from rag_utils import search_teacher_notes, format_teacher_notes, search_grammar, format_grammar_info
        
        # 1. Grammar DB lookup
        grammar_point = search_grammar(req.topic, req.level)
        if grammar_point:
            reference_text += format_grammar_info(grammar_point)
            
        # 2. Teacher Notes Vector Search (AI Sensei consistency)
        # Search by topic if possible, otherwise by category
        query = req.topic if req.topic and len(req.topic) > 1 else req.category
        notes = search_teacher_notes(query)
        if notes:
            reference_text += format_teacher_notes(notes)
            
    except Exception as e:
        print(f"Error loading RAG context (Teacher Notes/Grammar DB): {e}")


    # Determine Strategy: Aki Style (Loop) vs Legacy (Batch)
    # Aki Style is for Grammar/Vocab/Quiz (Single question focused)
    # Legacy is for Reading (Passage based)
    use_aki_style = req.category not in ["reading", "読解"]

    questions_data = []

    if use_aki_style:
        print(f"Generating {count} questions using Aki Style Loop...")
        # Loop to generate questions one by one
        for i in range(count):
            try:
                # Use Jay's Aki Style Prompt
                prompt = get_aki_style_prompt(req.level, req.topic, req.category, loop_index=i, total_count=count, reference_text=reference_text)
                
                # Model check (Constraint to 2 models)
                target_model = req.model
                if target_model not in ["gpt-4o", "gemini-2.0-flash"]:
                    target_model = "gpt-4o" # Strict fallback

                is_openai = target_model.startswith("gpt-")
                is_gemini = target_model.startswith("gemini")
                result_json = {}

                if is_openai:
                    client = get_openai_client()
                    if not client:
                        print("Error: OpenAI client could not be initialized")
                        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
                    
                    print(f"Sending request to OpenAI ({req.model})...")
                    try:
                        response = await client.chat.completions.create(
                            model=target_model,
                            messages=[
                                {"role": "system", "content": "You are a specific Japanese language quiz generator. Output must be valid JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.2,
                            response_format={"type": "json_object"}
                        )
                        content = response.choices[0].message.content
                        print(f"=== OpenAI Response ===\n{content[:100]}...\n===")
                        cleaned_content = clean_json_string(content)
                        result_json = json.loads(cleaned_content)
                    except Exception as e:
                        print(f"OpenAI Error: {e}")
                        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
                elif is_gemini:
                    gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
                    if not gemini_key:
                        raise HTTPException(status_code=503, detail="Gemini API key not configured")
                    
                    try:
                        genai.configure(api_key=gemini_key)
                        model = genai.GenerativeModel(target_model)
                        print(f"Sending request to Gemini ({req.model})...")
                        # Gemini 1.5 supports JSON response schema via generation_config
                        response = model.generate_content(
                            prompt,
                            generation_config={"response_mime_type": "application/json", "temperature": 0.2}
                        )
                        content = response.text
                        print(f"=== Gemini Response ===\n{content[:100]}...\n===")
                        cleaned_content = clean_json_string(content)
                        result_json = json.loads(cleaned_content)
                    except Exception as e:
                        error_str = str(e)
                        if "429" in error_str or "quota" in error_str.lower():
                            print(f"Gemini Quota Exceeded (429). Falling back to GPT-4o...")
                            # Fallback to OpenAI
                            client = get_openai_client()
                            if not client:
                                raise HTTPException(status_code=503, detail="Gemini Quota Exceeded and OpenAI not configured.")
                            
                            response = await client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": "You are a Japanese language quiz generator. Output must be valid JSON. (Gemini Fallback)"},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.2,
                                response_format={"type": "json_object"}
                            )
                            content = response.choices[0].message.content
                            result_json = json.loads(clean_json_string(content))
                        else:
                            print(f"Gemini Error: {e}")
                            raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")

                else:
                    # Invalid or local model (already handled by target_model set to gpt-4o)
                    raise HTTPException(status_code=400, detail="Unsupported model")
                
                # --- Normalize Data ---
                # Check if wrapped in list
                if isinstance(result_json, list):
                    result_json = result_json[0] # Take first if list
                
                # Normalize 'answer' to 'correctIndex'
                if "answer" in result_json and "options" in result_json:
                    try:
                        idx = result_json["options"].index(result_json["answer"])
                        result_json["correctIndex"] = idx
                    except ValueError:
                        # Fallback if answer string doesn't match options exactly
                        result_json["correctIndex"] = 0
                
                # Add title/type metadata
                result_json["type"] = "quiz"
                
                questions_data.append(result_json)

            except HTTPException as he:
                raise he
            except Exception as e:
                print(f"Error generating question {i+1}: {e}")
                # Continue loop even if one fails
                continue
    
    else:
        # Legacy Batch Logic for Reading (Keep existing flow roughly)
        # We invoke the prompt once for 'count' questions (though Reading is usually 1 text)
        print("Generating Reading questions using Legacy Batch...")
        
        # ... (Include RAG/PDF context only for Reading if needed, or omit for now to keep simple)
        # For compatibility, let's just use get_quiz_prompt which handles Reading
        prompt = get_quiz_prompt(req.category, req.level, count, reference_text, None, req.include_image)
        
        # Model check (Reading)
        target_model = req.model
        if target_model not in ["gpt-4o", "gemini-2.0-flash"]:
            target_model = "gpt-4o"

        is_openai = target_model.startswith("gpt-")
        if is_openai:
            client = get_openai_client()
            if not client:
                 raise HTTPException(status_code=503, detail="OpenAI API key not configured")
            
            print(f"Sending request to OpenAI ({req.model}) for Reading...")
            try:
                response = await client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": "You are a Japanese teacher. Output must be valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                raw_content = response.choices[0].message.content
                print(f"=== OpenAI Reading Response ===\n{raw_content[:100]}...\n===")
            except Exception as e:
                print(f"OpenAI Reading Error: {e}")
                raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")
        elif req.model.startswith("gemini"):
            gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
            if not gemini_key:
                raise HTTPException(status_code=503, detail="Gemini API key not configured")
            
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(target_model)
                print(f"Sending request to Gemini ({req.model}) for Reading...")
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.2}
                )
                raw_content = response.text
                print(f"=== Gemini Reading Response ===\n{raw_content[:100]}...\n===")
            except Exception as e:
                print(f"Gemini Reading Error: {e}")
                raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported model")
        
        # Parse JSON
        try:
            cleaned = clean_json_string(raw_content)
            data = json.loads(cleaned)
            if isinstance(data, dict):
                keys = list(data.keys())
                if len(keys) == 1 and isinstance(data[keys[0]], list):
                    data = data[keys[0]]
                else:
                    data = [data]
            questions_data = data
        except Exception as e:
            print(f"Legacy Parse Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response")

    # --- Common Post-Processing: Images ---
    if req.include_image and questions_data:
        for item in questions_data:
            # For Aki style, we didn't ask for image description, so we might skip or auto-generate
            # New Aki prompt doesn't output 'image_description'. 
            # If user wants images, we might need a separate call or just skip for now to adhere to Jay's strict format.
            pass 
            # (Optional: Add image generation logic back if needed, but Jay's prompt is text-only for now)
    
    return questions_data

@app.post("/api/mock-test")
async def generate_mock_test(req: MockTestRequest, current_user: dict = Depends(get_current_user)):
    # Block feature for standard users
    if current_user.get("plan_type", "standard") == "standard":
        raise HTTPException(status_code=403, detail="Standardプランではこの機能は利用できません。Proプラン以上へアップグレードしてください。")
        
    # 1. Get Image
    data, error = get_random_page_image(req.level)
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    # We'll use the dynamic get_openai_client for OpenAI, but need gemini_key below just in case.
    
    prompt = f"""
    You are a Japanese exam digitizer. 
    Analyze this image from a JLPT {req.level} exam.
    
    Task:
    1. Identify any "Quiz Questions" or "Reading Tasks" on this page.
    2. Extract them into a structured JSON format.
    3. If there is a reading passage, include it in the "question" field.
    4. Provide the correct answer and a brief explanation for each.
    
    Return ONLY valid JSON (no markdown frame):
    [
      {{
        "question": "Question text...",
        "options": ["A", "B", "C", "D"],
        "correctIndex": 0,
        "explanation": "Why it is correct..."
      }}
    ]
    
    If no questions are found (e.g. cover page), return an empty list [].
    """
    
    # Model validation
    target_model = req.model
    if target_model not in ["gpt-4o", "gemini-2.0-flash"]:
        target_model = "gpt-4o"

    try:
        if target_model.startswith("gemini"):
            gemini_key = config.get_config().get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                 raise HTTPException(status_code=401, detail="Gemini API Key not configured")
            
            genai.configure(api_key=gemini_key)
            model_instance = genai.GenerativeModel(req.model)
            
            response = model_instance.generate_content([
                prompt,
                {
                    "mime_type": "image/png", 
                    "data": data['image_base64']
                }
            ], generation_config={"response_mime_type": "application/json", "temperature": 0.2})
            
            content = response.text
        else:
            client = get_openai_client()
            if not client:
                raise HTTPException(status_code=401, detail="OpenAI API Key not configured")
            
            vision_model = "gpt-4o"
            
            response = await client.chat.completions.create(
                model=vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{data['image_base64']}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1500,
            )
            content = response.choices[0].message.content
            
        clean = re.sub(r'```json\s*|\s*```', '', content).strip()
        
        try:
            questions = json.loads(clean)
        except:
            questions = []
            
        return {
            "image_base64": data['image_base64'],
            "filename": data['filename'],
            "page": data['page'],
            "questions": questions
        }
    except Exception as e:
        print(f"Mock Test Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inquiry")
async def send_inquiry(req: InquiryRequest):
    recipient = os.getenv("INQUIRY_RECIPIENT_EMAIL", "aki.t901@gmail.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if not smtp_user or not smtp_pass:
        # Fallback to logging if SMTP not configured yet
        print(f"\n[INQUIRY LOG] From: {req.email} ({req.name})")
        print(f"Subject: {req.subject}")
        print(f"Message: {req.message}\n")
        return {"message": "お問い合わせを送信しました（管理者ログに記録）"}

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient
        msg['Subject'] = f"[Verba Inquiry] {req.subject}"
        
        body = f"Name: {req.name}\nEmail: {req.email}\n\nMessage:\n{req.message}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        
        return {"message": "お問い合わせを送信しました。"}
    except Exception as e:
        print(f"Inquiry Email Error: {e}")
        raise HTTPException(status_code=500, detail="メールの送信に失敗しました。")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
