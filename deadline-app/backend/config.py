from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 8

    model_config = {"env_file": ".env"}


settings = Settings()
