from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-change-me"
    DB_URL: str = "sqlite:///./app.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "*"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()