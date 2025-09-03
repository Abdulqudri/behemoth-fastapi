# type: ignore
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The settings for the application."""

    model_config = SettingsConfigDict(env_file=".env")

    # App
    DEBUG: bool = os.environ.get("DEBUG")

    # Logfire
    LOGFIRE_TOKEN: str | None = os.environ.get("LOGFIRE_TOKEN")

    # DB Settings
    POSTGRES_DATABASE_URL: str = os.environ.get("POSTGRES_DATABASE_URL")

    # REDIS
    REDIS_BROKER_URL: str = os.environ.get("REDIS_BROKER_URL")
    
    SECRET_KEY: str =  os.environ.get("SECRET_KEY") # should come from .env
    ALGORITHM: str = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")


@lru_cache
def get_settings():
    """This function returns the settings obj for the application."""
    return Settings()




print(f"--- ATTEMPTING TO USE DATABASE URL: '{get_settings().POSTGRES_DATABASE_URL}' ---")
