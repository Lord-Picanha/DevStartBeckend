from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chatbot AI API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    OPENAI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./chatbot.db"

    class Config:
        env_file = ".env"

settings = Settings()