from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    tts_provider: str = "aliyun"  # aliyun | volcengine | mock
    lip_sync_provider: str = "heygen"
    storage_dir: str = "storage"
    public_base_url: str = "http://localhost:8000"
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_appkey: str = ""
    aliyun_region: str = "ap-southeast-1"
    heygen_api_key: str = ""
    heygen_avatar_id: str = ""
    volcengine_app_id: str = ""
    volcengine_token: str = ""
    volcengine_cluster: str = ""
    volcengine_voice_type: str = "BV001_streaming"
    settings_secret_key: str = "dev-secret"


settings = Settings()
