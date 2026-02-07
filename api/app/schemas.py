from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    raw_text: str


class ProjectOut(BaseModel):
    id: int
    title: str


class ParsedScript(BaseModel):
    scenes: list


class ShotOut(BaseModel):
    shot_id: int
    shot_index: int
    description: str
    duration_sec: int


class DialogueIn(BaseModel):
    speaker: str
    text: str


class DialogueOut(BaseModel):
    id: int
    speaker: str
    text: str
    audio_path: Optional[str] = None


class DialogueUpdate(BaseModel):
    dialogues: List[DialogueIn]


class RenderOut(BaseModel):
    render_id: int


class RenderStatus(BaseModel):
    status: str
    progress: int
    output_video_path: Optional[str] = None


class ProjectSettingsOut(BaseModel):
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    avatar_image_url: Optional[str] = None
    avatar_iv_image_key: Optional[str] = None
    background_style: Optional[str] = None
    use_shots_for_avatar_iv: Optional[bool] = True


class ProjectSettingsUpdate(BaseModel):
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    avatar_iv_image_key: Optional[str] = None
    background_style: Optional[str] = None
    use_shots_for_avatar_iv: Optional[bool] = None


class SystemSettingsOut(BaseModel):
    tts_provider: str
    enable_heygen: bool
    enable_avatar_iv: bool
    aliyun_access_key_id_masked: Optional[str] = None
    aliyun_access_key_secret_masked: Optional[str] = None
    aliyun_appkey_masked: Optional[str] = None
    heygen_api_key_masked: Optional[str] = None
    volcengine_app_id_masked: Optional[str] = None
    volcengine_token_masked: Optional[str] = None
    volcengine_cluster: Optional[str] = None
    volcengine_voice_type: Optional[str] = None


class SystemSettingsUpdate(BaseModel):
    tts_provider: Optional[str] = None
    enable_heygen: Optional[bool] = None
    enable_avatar_iv: Optional[bool] = None
    aliyun_access_key_id: Optional[str] = None
    aliyun_access_key_secret: Optional[str] = None
    aliyun_appkey: Optional[str] = None
    heygen_api_key: Optional[str] = None
    volcengine_app_id: Optional[str] = None
    volcengine_token: Optional[str] = None
    volcengine_cluster: Optional[str] = None
    volcengine_voice_type: Optional[str] = None
