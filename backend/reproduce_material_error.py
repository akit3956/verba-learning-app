import requests
import json

url = "http://localhost:8000/api/materials/generate"
payload = {
    "category": "reading",
    "level": "N4",
    "topic": "Travel",
    "model": "gemini-flash-latest",
    "reference_text": ""
}

try:
    print(f"Sending request to {url}...")
    resp = requests.post(url, json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
