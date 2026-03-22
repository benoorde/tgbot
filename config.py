from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    CRYPTO_BOT_TOKEN: str
    PRIVATE_CHANNEL_ID: int
    PRICE_STARS: int
    PRICE_USDT: float
    
    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8080
    PORT: int | None = None  
    BASE_WEBHOOK_URL: str = ""


settings = Settings()
