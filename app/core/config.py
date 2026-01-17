from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Docx Converter Service"
    DATABASE_URL: str = "postgresql://user:password@db:5432/converter_db"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    SHARED_DIR: str = "/data"

    class Config:
        env_file = ".env"

settings = Settings()