import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

#Load environment variables from a .env file, if available
load_dotenv()

#Define the directory and default SQLite database path
top_dir = Path(__file__).resolve().parents[0]
db_dir = top_dir / "db"
sqlite_db_name = "tesis.db"
sqlite_db_path = str(db_dir / sqlite_db_name)

db_dir.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    DB_URI: str | None = os.getenv('DB_URI') # Full connection string (takes priority)
    DB_HOST: str | None = os.getenv('DB_HOST')
    DB_NAME: str | None = os.getenv('DB_NAME')
    DB_PORT: str | None = os.getenv('DB_PORT')
    DB_USER: str | None = os.getenv('DB_USER')
    DB_PASS: str | None = os.getenv('DB_PASSWORD')

    SQLITE_PATH: str = sqlite_db_path

    def __is_valid_db_uri(self) -> bool:
        if self.DB_URI:
            return self.DB_URI.startswith(("postgresql://", "mysql://", "postgresql+psycopg2://"))

    @property
    def DATABASE_URI(self) -> str:
        if self.__is_valid_db_uri():
            return self.DB_URI
        
        if all([self.DB_HOST, self.DB_NAME, self.DB_PORT, self.DB_USER, self.DB_PASS]):
            return (f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:"
                    f"{self.DB_PORT}/{self.DB_NAME}")
        
        return f"sqlite:///{self.SQLITE_PATH}"
    
    class Config:
        case_sensitive: True

logger = logging.getLogger(__name__)

@lru_cache
def get_settings():
    logger.info("Loading application settings...")
    return Settings()

settings = get_settings()