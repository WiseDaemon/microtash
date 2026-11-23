import os
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    APP_NAME: str = "Microstash — The Mental Model Gym"
    APP_TAGLINE: str = "Stop hoarding ideas. Start wiring them into your brain."
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Authentication & Session Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "microstash_vault_jwt_secret_key_2026_super_secure_token")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_DAYS: int = int(os.getenv("JWT_EXPIRY_DAYS", "30"))
    
    # API Keys
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # AI Engine Defaults
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "nvidia")
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
    _db_path: Optional[Path] = None

    @property
    def DB_PATH(self) -> Path:
        """
        Dynamically resolves the active SQLite database path with strict priority:
        1. Explicit programmatic override on settings instance (e.g. settings.DB_PATH = ...)
        2. Environment variables: MICROSTASH_DB_PATH or TEST_DATABASE_PATH
        3. DATABASE_URL (if formatted as sqlite:///path/to/db)
        4. Default production database: data/microstash.db
        """
        if self._db_path is not None:
            return Path(self._db_path)

        env_override = os.getenv("MICROSTASH_DB_PATH") or os.getenv("TEST_DATABASE_PATH")
        if env_override:
            return Path(env_override)

        if self.DATABASE_URL and self.DATABASE_URL.startswith("sqlite:///"):
            return Path(self.DATABASE_URL.replace("sqlite:///", ""))

        return self.DATA_DIR / "microstash.db"

    @DB_PATH.setter
    def DB_PATH(self, value: Optional[Union[str, Path]]) -> None:
        """Allows test fixtures and CLI runners to dynamically switch database targets."""
        self._db_path = Path(value) if value is not None else None

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
