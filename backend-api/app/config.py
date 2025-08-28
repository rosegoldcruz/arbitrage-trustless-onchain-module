from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "production"
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    STREAM_NAMESPACE: str = "atom"
    CORS_ORIGINS: str = "https://smart4technology.com,https://api.smart4technology.com"
    MEV_STREAM_KEY: str | None = None
    TRIANGULAR_STREAM_KEY: str | None = None
    LIQUIDITY_STREAM_KEY: str | None = None
    STAT_ARB_STREAM_KEY: str | None = None
    VOLATILITY_STREAM_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=("/etc/atom/backend-api.env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
missing = [k for k in ["REDIS_HOST","STREAM_NAMESPACE","CORS_ORIGINS"] if not getattr(settings, k, None)]
if missing:
    raise RuntimeError(f"Missing required env keys: {', '.join(missing)}")