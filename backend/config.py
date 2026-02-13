import os
from dotenv import load_dotenv

load_dotenv()

# Global config storage
# Initializes with values from .env
global_config = {
    "model": "gemma2",
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "gemini_api_key": os.getenv("GEMINI_API_KEY", "")
}

def get_config():
    return global_config

def update_config(key, value):
    if key in global_config:
        global_config[key] = value
