from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Platform Bot Configuration
    platform_bot_token: str
    jwt_secret: str
    encryption_key: str
    
    # Database Configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # MinIO Configuration
    minio_root_user: str
    minio_root_password: str
    minio_bucket_name: str
    minio_endpoint: str = "minio:9000"
    minio_secure: bool = False
    
    # Application Configuration
    domain: str = "mgx.dev"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()