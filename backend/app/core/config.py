from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Finder"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://89.169.150.10",
        "http://89.169.150.10:3000",
        "http://89.169.150.10:8000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "db"  # Changed from localhost to db for Docker
    POSTGRES_USER: str = "postgres"  # Changed to postgres user
    POSTGRES_PASSWORD: str = "postgres"  # Changed to postgres password
    POSTGRES_DB: str = "project_finder"
    SQLALCHEMY_DATABASE_URI: str | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, any]) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # Redis
    REDIS_HOST: str = "redis"  # Changed from localhost to redis for Docker
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    # JWT
    SECRET_KEY: str = "project-finder-secret-key-2024"  # Изменено для продакшена
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Увеличено до 60 минут

    # ML Model
    MODEL_NAME: str = "all-MiniLM-L6-v2"  # Default sentence transformer model

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 