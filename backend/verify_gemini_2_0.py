import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

try:
    models_to_test = ["gemini-2.5-flash", "gemini-flash-latest"]
    for m in models_to_test:
        try:
            print(f"\nGeneratig content with {m}...")
            model = genai.GenerativeModel(m)
            response = model.generate_content("Hello")
            print(f"Response from {m}: {response.text}")
            print(f"SUCCESS with {m}!")
            break
        except Exception as e:
            print(f"Failed {m}: {e}")

except Exception as e:
    print(f"Error: {e}")
