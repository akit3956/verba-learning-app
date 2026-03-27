import requests
import json
import os

# AIチューターのRAG機能（ベクトル検索）を検証するためのスクリプト
# ※このテストを実行するには、backendが起動しており、DATABASE_URLとOPENAI_API_KEYが設定されている必要があります。

BASE_URL = "http://localhost:8000"

def test_tutor_chat():
    url = f"{BASE_URL}/api/tutor/chat"
    
    # テスト用のメッセージ（教案に関連しそうな内容）
    payload = {
        "message": "「〜ように」の使い方について教えてください。",
        "model": "gpt-4o"
    }
    
    # 認証トークンが必要な場合は取得（ここではダミーまたは既存のトークンを想定）
    # API呼び出しをエミュレート
    print(f"Testing AI Tutor Chat RAG (Miss Kaplan): {url}")
    print(f"Query: {payload['message']}")
    
    try:
        # 実際のリクエスト（現状は環境が整っていないためコメントアウト）
        # token = "YOUR_JWT_TOKEN"
        # headers = {"Authorization": f"Bearer {token}"}
        # resp = requests.post(url, json=payload, headers=headers)
        # print(f"Status: {resp.status_code}")
        # print(f"Response: {resp.json().get('reply')[:200]}...")
        print("Note: Run 'backend/ingest_notes.py' first to populate the vector database.")
        print("Then use the frontend or cURL to test the real chat flow.")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_tutor_chat()
    print("\n[検証ポイント]")
    print("1. backend/teacher_notes/ にファイルを配置しましたか？")
    print("2. Supabaseで schema.sql を実行しましたか？")
    print("3. python backend/ingest_notes.py を実行しましたか？")
