from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Docx Converter Service"
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    SHARED_DIR: str = "/data"
    
    API_KEYS: str = "docx_public_web_2026"
    PUBLIC_API_KEY: str = "docx_public_web_2026"

    class Config:
        env_file = ".env"
       
        extra = "ignore" 

settings = Settings()