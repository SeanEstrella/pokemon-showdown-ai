import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    NASH_USERNAME: str = os.getenv("NASH_USERNAME") or ""
    if not NASH_USERNAME:
        raise ValueError("NASH_USERNAME environment variable is required")
    NASH_PASSWORD: str = os.getenv("NASH_PASSWORD") or ""
    if not NASH_PASSWORD:
        raise ValueError("NASH_PASSWORD environment variable is required")
    
    MAX_USERNAME: str = os.getenv("MAX_USERNAME") or ""
    if not MAX_USERNAME:
        raise ValueError("MAX_USERNAME environment variable is required")
    MAX_PASSWORD: str = os.getenv("MAX_PASSWORD") or ""
    if not MAX_PASSWORD:
        raise ValueError("MAX_PASSWORD environment variable is required")
    
    GEN_1_FORMAT: str = "gen1randombattle"
    LOG_LEVEL=20


settings = Settings()
