from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://darukaa:darukaa@localhost:5432/darukaa"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
