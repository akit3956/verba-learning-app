import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    # Testing known available models
    models_to_test = ["gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models_to_test:
        try:
            print(f"\nGenerating content with {m}...")
            response = client.models.generate_content(model=m, contents="Hello")
            print(f"Response from {m}: {response.text}")
            print(f"SUCCESS with {m}!")
            break
        except Exception as e:
            print(f"Failed {m}: {e}")

except Exception as e:
    print(f"Error: {e}")
