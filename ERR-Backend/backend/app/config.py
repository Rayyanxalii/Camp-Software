from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str

    # Optional operational settings
    ADMIN_PASSWORD: Optional[str] = None
    CREATE_DEFAULT_ADMIN: bool = False
    ALLOWED_ORIGINS: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()