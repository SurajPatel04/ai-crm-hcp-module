from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    groq_api_key: str = ""

    secret_key: str
    refresh_token_secret_key: str
    algorithm: str = "HS256"

    access_token_expire_time: int
    refresh_token_expire_time: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()