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
    app_name: str = "Mundo Negocio Dashboard API"
    app_version: str = "6.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Database
    database_url: str = Field(default="postgresql://localhost/mundonegocio")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379")
    
    # JWT
    jwt_secret_key: str = Field(default="change-this-to-a-secure-secret-key-min-32-chars")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3002",
            "https://localhost:3000"
        ]
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Cache
    cache_ttl_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton
    """
    return Settings()
