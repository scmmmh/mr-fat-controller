"""Access to the application settings."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class MqttSettings(BaseModel):
    """MQTT settings model."""

    host: str
    port: int = 8883
    username: str | None = None
    password: str | None = None
    tls: bool = True
    insecure_tls: bool = True


class Settings(BaseSettings):
    """Application settings model."""

    dsn: str
    mqtt: MqttSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="mfc_",
        env_nested_delimiter="_",
        extra="ignore",
    )


settings = Settings()  # pyright: ignore[reportCallIssue]
