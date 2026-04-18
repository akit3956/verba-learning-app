import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    for m in client.models.list():
        print(m.name)
            
    model_name = "gemini-2.0-flash"
    print(f"\nGenerating content with {model_name}...")
    response = client.models.generate_content(model=model_name, contents="Hello, can you hear me?")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
