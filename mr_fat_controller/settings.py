"""Access to the application settings."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings model."""

    dsn: str

    class Config:
        """Pydantic settings config."""

        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings().dict()
