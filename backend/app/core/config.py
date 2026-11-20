import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "BIJLI MITRA AI"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR}/bijli_mitra.db"
    )
    
    # Storage
    STORAGE_DIR: Path = WORKSPACE_DIR / "storage"
    UPLOAD_DIR: Path = STORAGE_DIR / "uploads"
    PROCESSED_DIR: Path = STORAGE_DIR / "processed"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bijli-mitra-secure-telangana-energy-key-2026")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # AI / LLM (Optional Gemini / local grounded generator)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
