from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 480

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_forte(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("jwt_secret deve ter pelo menos 32 caracteres")
        return v

    class Config:
        env_file = ".env"


settings = Settings()
