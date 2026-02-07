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
