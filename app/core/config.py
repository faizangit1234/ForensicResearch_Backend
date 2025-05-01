from pathlib import Path

from pydantic_settings import BaseSettings

DATA_FILE_PATH = Path("app/data/storage.csv")


class Settings(BaseSettings):
    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
