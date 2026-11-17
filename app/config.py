from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int = 60
    ACCESS_TOKEN_EXPIRES_IN: int = 30
    JWT_ALGORITHM: str = "RS256"

    CLIENT_ORIGIN: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file="./.env", extra="ignore")


settings = Settings()