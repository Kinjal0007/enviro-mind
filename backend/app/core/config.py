from typing import List
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EnviroMind"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Frontend URL
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "enviromind")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Copernicus API
    COPERNICUS_API_KEY: Optional[str] = os.getenv("COPERNICUS_API_KEY")
    
    # Galileo HAS
    GALILEO_HAS_ENABLED: bool = os.getenv("GALILEO_HAS_ENABLED", "False").lower() == "true"

    class Config:
        case_sensitive = True

settings = Settings() 