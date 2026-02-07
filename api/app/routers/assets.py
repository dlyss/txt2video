from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..settings import settings

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("/audio/{render_id}/{filename}")
def get_audio_asset(render_id: int, filename: str):
    base = Path(__file__).resolve().parents[1] / settings.storage_dir / "renders" / f"{render_id}"
    candidates = [
        base / filename,
        base / "tts" / filename,
    ]
    for target in candidates:
        if target.exists():
            return FileResponse(str(target), media_type="audio/wav")
    raise HTTPException(status_code=404, detail="audio not found")


@router.get("/avatar/{project_id}")
def get_avatar(project_id: int):
    storage = Path(__file__).resolve().parents[1] / settings.storage_dir / "avatars"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        target = storage / f"project_{project_id}{ext}"
        if target.exists():
            return FileResponse(str(target), media_type="image/*")
    raise HTTPException(status_code=404, detail="avatar not found")
