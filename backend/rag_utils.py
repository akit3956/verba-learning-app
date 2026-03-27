import json
import os
from typing import Optional, Dict, List

# Path to the grammar database
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "grammar_db.json")

def load_grammar_db() -> Dict:
    """Loads the grammar database from JSON."""
    if not os.path.exists(DB_PATH):
        return {"grammar_points": []}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading grammar DB: {e}")
        return {"grammar_points": []}

def search_grammar(topic: str, level: str = "") -> Optional[Dict]:
    """
    Searches for a grammar point that matches the topic.
    Simple keyword matching for now.
    """
    db = load_grammar_db()
    topic_normalized = topic.replace("〜", "").replace("~", "").strip()
    
    for point in db.get("grammar_points", []):
        # Check if the topic matches any keyword
        keywords = point.get("keywords", [])
        # Check if topic is contained in keywords OR keywords contained in topic
        # e.g. topic="〜ように" -> keyword="ように" matched
        for k in keywords:
            k_clean = k.replace("〜", "").replace("~", "")
            if k_clean in topic_normalized or topic_normalized in k_clean:
                # Optional: Filter by level if strictly required, but usually topic match is enough
                return point
    return None

def format_grammar_info(grammar_point: Dict) -> str:
    """
    Formats the grammar point data into a string for the LLM prompt.
    """
    if not grammar_point:
        return ""

    rules_str = "\n".join([f"- {r}" for r in grammar_point.get("rules", [])])
    good_ex = "\n".join([f"- {ex}" for ex in grammar_point.get("good_examples", [])])
    bad_ex = "\n".join([f"- {ex}" for ex in grammar_point.get("bad_examples", [])])

    return f"""
【公式文法辞書データ（遵守すること）】
■ 文法: {grammar_point.get('keywords', [''])[0]} ({grammar_point.get('jlpt_level', '')})
■ 意味: {grammar_point.get('meaning', '')}
■ 接続: {grammar_point.get('structure', '')}
■ 厳守ルール:
{rules_str}

■ 良い使用例（真似すること）:
{good_ex}

■ 悪い使用例（避けること）:
{bad_ex}
"""

def get_openai_embedding(text: str) -> List[float]:
    """Generates embedding for a given text using OpenAI."""
    from openai import OpenAI
    import config
    api_key = os.getenv("OPENAI_API_KEY") or config.get_config().get("openai_api_key")
    if not api_key:
        raise ValueError("OpenAI API key not found for embeddings.")
    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_teacher_notes(query: str, match_threshold: float = 0.3, match_count: int = 3) -> List[Dict]:
    """
    Searches teacher_embeddings table in Supabase via RPC or raw SQL.
    We use the match_teacher_notes function defined in schema.sql.
    """
    from database import get_db_connection
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=lambda *args, **kwargs: conn.cursor(*args, **kwargs))
        
        print(f"Searching teacher notes for: {query}")
        query_embedding = get_openai_embedding(query)
        
        # Call the RPC function defined in Supabase
        cur.execute(
            "SELECT content, metadata, similarity FROM match_teacher_notes(%s, %s, %s)",
            (query_embedding, match_threshold, match_count)
        )
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} matching chunks.")
        results = []
        for row in rows:
            results.append({
                "content": row[0],
                "metadata": row[1],
                "similarity": row[2]
            })
        
        cur.close()
        conn.close()
        return results
    except Exception as e:
        import traceback
        print(f"Error searching teacher notes: {e}")
        print(traceback.format_exc())
        return []

def format_teacher_notes(notes: List[Dict]) -> str:
    """Formats retrieved chunks into a context string."""
    if not notes:
        return ""
    
    header = "\n【ミス・キャプランの教案（バイブル）より抽出された関連資料】\n"
    body = ""
    for note in notes:
        source = note['metadata'].get('source', 'Unknown')
        body += f"--- Source: {source} ---\n{note['content']}\n"
    
    return header + body + "\n※上記の教案内容に100%忠実に、ミス・キャプランのメソッドに従って回答してください。\n"
