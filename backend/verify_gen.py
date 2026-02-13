import requests
import json
import time

URL = "http://localhost:8000/generate"

def test_generation():
    print("Testing N5 Grammar Generation (Aki Style)...")
    payload = {
        "category": "grammar",
        "level": "N3",
        "topic": "general",
        "mode": "single",
        "model": "gpt-4o", 
        "include_image": False
    }
    
    # Use a simpler model if gemma2 isn't running, but user had it running before.
    # If this fails, we'll see the error.
    
    try:
        start = time.time()
        print(f"Sending request to {URL}...")
        response = requests.post(URL, json=payload, timeout=120)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if isinstance(data, list) and len(data) > 0:
                q = data[0]
                if "question" in q and "options" in q and "correctIndex" in q:
                    print("\n[SUCCESS] Response checks out!")
                else:
                    print("\n[WARNING] Response format missing keys.")
            else:
                print("\n[WARNING] Empty list or invalid format.")
        else:
            print(f"\n[ERROR] Request failed: {response.text}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")

if __name__ == "__main__":
    test_generation()
