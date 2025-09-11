# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

class Settings:
    # LiveKit
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    LIVEKIT_URL = os.getenv("LIVEKIT_URL")
    
    # OpenAI (NOT Azure)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # ElevenLabs
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    
    # Task storage
    TASKS_FILE = "data/tasks.json"

settings = Settings()