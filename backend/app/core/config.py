import os
from dataclasses import dataclass
from pathlib import Path


def required(key: str) -> str:
    value = os.environ.get(key)
    if value is None or value == "":
        raise ValueError(f"Required environment variable '{key}' is not set.")
    return value


def to_int(key: str, default: int | None = None) -> int:
    value = os.environ.get(key)
    if value is None or value == "":
        if default is not None:
            return default
        value = required(key)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable '{key}' must be a valid integer."
        ) from exc


def to_list(key: str) -> list[str]:
    value = required(key)
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Config:
    #db
    POSTGRES_HOST: str = required("POSTGRES_HOST")
    POSTGRES_PORT: int = to_int("POSTGRES_PORT")
    POSTGRES_DB: str = required("POSTGRES_DB")
    POSTGRES_USER: str = required("POSTGRES_USER")
    POSTGRES_PASSWORD: str = required("POSTGRES_PASSWORD")

    #redis
    REDIS_HOST: str = required("REDIS_HOST")
    REDIS_PORT: int = to_int("REDIS_PORT",6379)
    REDIS_DB: str = to_int("REDIS_DB",0)
    REDIS_PASSWORD: str = required("REDIS_PASSWORD")

    #JWT
    JWT_SECRET: str = required("JWT_SECRET")
    TOKEN_EXPIRY_IN_MIN: int = to_int("TOKEN_EXPIRY_IN_MIN", 30)
    HASHING_ALGORITHM: str = os.getenv("HASHING_ALGORITHM", "HS256")

    #logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL","DEBUG")
    APP_ENV: str = os.getenv("APP_ENV","DEV")
    
    #CORS 
    CORS_ORIGIN: str = os.getenv("CORS_ORIGIN")

    @property
    def get_postgres_url(self):
        return (
             f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def get_redis_url(self):
       if self.REDIS_PASSWORD:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
       else:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


Settings = Config()
