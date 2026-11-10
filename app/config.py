import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    APP_NAME: str = "Microstash — The Mental Model Gym"
    APP_TAGLINE: str = "Stop hoarding ideas. Start wiring them into your brain."
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API Keys
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # AI Engine Defaults
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Database (Defaults to SQLite; supports Supabase / Neon / PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Cloud Storage (Supports Cloudflare R2 / AWS S3 / local fallback)
    STORAGE_BUCKET_URL: str = os.getenv("STORAGE_BUCKET_URL", "")
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    AUDIO_DIR: Path = DATA_DIR / "audio"
    DB_PATH: Path = DATA_DIR / "microstash.db"

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
