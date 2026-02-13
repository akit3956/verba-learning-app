import requests
import json
import time

URL = "http://localhost:8000/generate"

def test_gemini():
    print("Testing N3 Grammar Generation with Gemini 1.5 Flash...")
    payload = {
        "category": "grammar",
        "level": "N3",
        "topic": "general",
        "mode": "single",
        "model": "gemini-flash-latest", 
        "include_image": False
    }
    
    try:
        start = time.time()
        print(f"Sending request to {URL}...")
        response = requests.post(URL, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if isinstance(data, list) and len(data) > 0:
                print("\n[SUCCESS] Gemini Generated Data!")
            else:
                print("\n[WARNING] Empty list or invalid format.")
        else:
            print(f"\n[ERROR] Request failed: {response.text}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")

if __name__ == "__main__":
    test_gemini()
