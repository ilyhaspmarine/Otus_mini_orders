from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os

BASE_DIR = Path(__file__).parent

class DbSettings(BaseModel):
    driver: str = "postgresql+" + os.getenv("DB_DRIVER_ASYNC", "asyncpg")
    username: str = os.getenv("DB_USER", "username")
    password: str = os.getenv("DB_PASSWORD", "password")
    host: str = os.getenv("DB_HOST", "host.docker.internal")
    port: str = os.getenv("DB_PORT", "5432")
    database: str = os.getenv("DB_NAME", "order")

# class RollbackJWT(BaseModel):
#     public_key_path: Path =  BASE_DIR /os.getenv("JWT_PUBLIC_PATH", "./etc/keys/rollback/public.pem")
#     algorithm: str = os.getenv("JWT_ALGORITH", "RS256")

class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    # rollback_jwt: RollbackJWT = RollbackJWT()

settings = Settings()