from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MundoNegocio API"
    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
