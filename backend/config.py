import os
import json
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    default_config = {
        "model": "gemma2",
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "gemini_api_key": os.getenv("GEMINI_API_KEY", "")
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                default_config.update(saved)
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

global_config = load_config()

def get_config():
    return global_config

def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(global_config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def update_config(key, value):
    if key in global_config:
        global_config[key] = value
        save_config()
