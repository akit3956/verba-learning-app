import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            
    model_name = "gemini-1.5-flash" # Trying a known stable model first
    print(f"\nGeneratig content with {model_name}...")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, can you hear me?")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
