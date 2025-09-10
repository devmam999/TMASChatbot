"""
Configuration utilities for loading environment variables
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Anthropic Claude API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-1-20250805")
    
    # Google GenAI API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,https://tmas-internship.vercel.app").split(",")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MEDIA_DIR: str = os.getenv("MEDIA_DIR", "./media")
    
    # Manim Configuration
    MANIM_OUTPUT_DIR: str = os.getenv("MANIM_OUTPUT_DIR", "./media")
    MANIM_QUALITY: str = os.getenv("MANIM_QUALITY", "medium_quality")
    MANIM_FRAME_RATE: int = int(os.getenv("MANIM_FRAME_RATE", "30"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        if not cls.GEMINI_API_KEY:
            # print("Warning: GEMINI_API_KEY is not set. Some features may not work.")
            raise ValueError("GEMINI_API_KEY is required")
        return True


# Create global settings instance
settings = Settings() 