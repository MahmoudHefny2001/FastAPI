from pydantic import BaseSettings


class Settings(BaseSettings):
    access_token_expire_minutes: int
    database_password: str
    database_host: str
    database_user: str
    database_port: str
    database_name: str
    secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


settings = Settings()