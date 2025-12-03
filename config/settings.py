"""
Configuración de la aplicación
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Settings de la aplicación"""
    
    # App
    APP_NAME: str = "Mundo Negocio Dashboard API"
    APP_VERSION: str = "6.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://localhost/mundonegocio")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    
    # JWT
    JWT_SECRET_KEY: str = Field(default="change-this-to-a-secure-secret-key-min-32-chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "https://localhost:3000"
        ]
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache
    CACHE_TTL_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton
    """
    return Settings()
