import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OpenAI Configuration (for LangGraph LLM)
    OPENAI_API_KEY: str
    
    # Google Cloud Configuration (for STT)
    GOOGLE_APPLICATION_CREDENTIALS: str
    
    # ElevenLabs Configuration (for TTS)
    ELEVEN_API_KEY: str
    
    # LiveKit Configuration
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
        case_sensitive=True,
        extra='ignore'  # Allow extra environment variables
    )

settings = Settings()
