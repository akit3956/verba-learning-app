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
