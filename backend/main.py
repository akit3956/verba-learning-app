from fastapi import FastAPI, HTTPException
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

# New Modules (Trigger Reload)
from database import init_db
from routers import wallet, materials, auth
import config
from pdf_utils import get_random_page_image
from pdf_context import load_context_for_level

class ConfigUpdate(BaseModel):
    model: str
    openai_api_key: str = ""
    gemini_api_key: str = ""

load_dotenv()

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local network access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    category: str  # "grammar", "vocab", "reading"
    level: str     # "N5", "N4", "N3", "N2", "N1"
    topic: str = ""
    mode: str = "single" # "single", "small_test", "mock_test"
    model: str = "gemma2"
    include_image: bool = False 

class MockTestRequest(BaseModel):
    level: str
    model: str = "gpt-4o"
    api_key: str = ""

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.get("/config")
async def get_config_endpoint():
    return config.get_config()

@app.post("/config")
async def update_config_endpoint(update: ConfigUpdate):
    config.update_config("model", update.model)
    config.update_config("openai_api_key", update.openai_api_key)
    config.update_config("gemini_api_key", update.gemini_api_key)
    return {"message": "Config updated", "config": config.get_config()}

@app.get("/models")
async def get_models():
    models = []
    
    # Always add OpenAI models as options (Validation happens at generation time)
    models.append({"name": "gpt-4o", "type": "cloud", "size": "OpenAI"})
    models.append({"name": "gpt-4-turbo", "type": "cloud", "size": "OpenAI"})
    models.append({"name": "gpt-3.5-turbo", "type": "cloud", "size": "OpenAI"})
    models.append({"name": "gemini-2.5-flash", "type": "cloud", "size": "Google"})
    models.append({"name": "gemini-2.0-flash", "type": "cloud", "size": "Google"})
    models.append({"name": "gemini-flash-latest", "type": "cloud", "size": "Google"})

    
    # Add Ollama models
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(OLLAMA_TAGS_URL, timeout=2.0)
            if resp.status_code == 200:
                ollama_models = resp.json().get("models", [])
                for m in ollama_models:
                    models.append({
                        "name": m.get("name", ""),
                        "type": "local",
                        "size": m.get("size", "Unknown")
                    })
    except Exception as e:
        print(f"Ollama error: {e}")
    
    return {"models": models}

import rag_utils # Import the RAG module

@app.post("/generate")
async def generate_quiz(req: GenerateRequest):
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
                prompt = get_aki_style_prompt(req.level, req.topic, req.category)
                
                # --- LLM Call ---
                is_openai = req.model.startswith("gpt-")
                is_gemini = req.model.startswith("gemini")
                result_json = {}

                if is_openai:
                    if not openai_client:
                        raise HTTPException(status_code=503, detail="OpenAI API key not configured")
                    
                    response = await openai_client.chat.completions.create(
                        model=req.model,
                        messages=[
                            {"role": "system", "content": "You are a specific Japanese language quiz generator."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2, # Lower temperature for precision as requested
                        response_format={"type": "json_object"} # Enforce JSON
                    )
                    content = response.choices[0].message.content
                    result_json = json.loads(content)
                elif is_gemini:
                    gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
                    if not gemini_key:
                        raise HTTPException(status_code=503, detail="Gemini API key not configured")
                    
                    try:
                        genai.configure(api_key=gemini_key)
                        model = genai.GenerativeModel(req.model)
                        print(f"Sending request to Gemini ({req.model})...")
                        # Gemini 1.5 supports JSON response schema via generation_config
                        response = model.generate_content(
                            prompt,
                            generation_config={"response_mime_type": "application/json", "temperature": 0.7}
                        )
                        content = response.text
                        print(f"=== Gemini Response ===\n{content}\n===")
                        result_json = json.loads(content)
                    except Exception as e:
                        print(f"Gemini Error: {e}")
                        raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")

                else:
                    # Ollama
                    payload = {
                        "model": req.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
                        resp.raise_for_status()
                        content = resp.json().get("response", "")
                        result_json = json.loads(content)
                
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
        
        is_openai = req.model.startswith("gpt-")
        if is_openai:
            if not openai_client:
                 raise HTTPException(status_code=503, detail="OpenAI API key not configured")
            
            response = await openai_client.chat.completions.create(
                model=req.model,
                messages=[{"role": "system", "content": "You are a Japanese teacher."}, {"role": "user", "content": prompt}],
                temperature=0.7
            )
            raw_content = response.choices[0].message.content
        elif req.model.startswith("gemini"):
            gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
            if not gemini_key:
                raise HTTPException(status_code=503, detail="Gemini API key not configured")
            
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(req.model)
                print(f"Sending request to Gemini ({req.model}) for Reading...")
                # Reading prompt might not be strict JSON, but let's try to enforce it if possible, 
                # or just get text and clean it like OpenAI/Ollama.
                # Since get_quiz_prompt asks for JSON, we use JSON mode.
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.3}
                )
                raw_content = response.text
                print(f"=== Gemini Reading Response ===\n{raw_content}\n===")
            except Exception as e:
                print(f"Gemini Reading Error: {e}")
                # Check for safety blocking if available in exception or response object (hard to get here if exception raised)
                raise HTTPException(status_code=500, detail=f"Gemini API Error: {e}")
        else:
            payload = {"model": req.model, "prompt": prompt, "format": "json", "stream": False}
            async with httpx.AsyncClient() as client:
                resp = await client.post(OLLAMA_URL, json=payload, timeout=120.0)
                raw_content = resp.json().get("response", "")
        
        # Parse JSON
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', raw_content).strip()
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
async def generate_mock_test(req: MockTestRequest):
    # 1. Get Image
    data, error = get_random_page_image(req.level)
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    current_api_key_openai = req.api_key or os.getenv("OPENAI_API_KEY") or config.get_config().get("openai_api_key")
    
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
    
    try:
        if req.model.startswith("gemini"):
            gemini_key = os.getenv("GEMINI_API_KEY") or config.get_config().get("gemini_api_key")
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
            if not current_api_key_openai:
                 raise HTTPException(status_code=401, detail="OpenAI API Key not configured")
            
            client = AsyncOpenAI(api_key=current_api_key_openai)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
