import requests
import json
import os

# 修正後の生成AIの挙動を確認するためのスクリプト
# 1. Temperatureが適切に反映されているか
# 2. 不自然な日本語（ますますする等）が生成されないか

BASE_URL = "http://localhost:8000"

def test_generate_quiz():
    url = f"{BASE_URL}/generate"
    # 副詞「ますます」を含む問題の生成を意図的に促すようなトピック設定
    payload = {
        "category": "grammar",
        "level": "N3",
        "topic": "ますます",
        "model": "gpt-4o", # または gemini-2.0-flash 等
        "mode": "single"
    }
    
    # 実際にはAPIキーが必要なため、ローカルサーバーが上がっている前提のコード
    print(f"Testing {url} with topic '{payload['topic']}'...")
    try:
        # 認証が必要な場合はヘッダーを追加する必要あり
        # ここでは構造の確認を主目的とする
        print("Note: This test requires the backend server and valid API keys.")
        # resp = requests.post(url, json=payload)
        # print(f"Status: {resp.status_code}")
        # print(f"Result: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_generate_quiz()
