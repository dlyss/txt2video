from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
from pathlib import Path

from ..db import SessionLocal
from ..models import Render
from ..schemas import RenderStatus

router = APIRouter(prefix="/api/renders", tags=["renders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{render_id}/status", response_model=RenderStatus)
def get_render_status(render_id: int, db: Session = Depends(get_db)):
    render = db.get(Render, render_id)
    if not render:
        raise HTTPException(status_code=404, detail="render not found")
    return RenderStatus(status=render.status, progress=render.progress, output_video_path=render.output_video_path)


@router.get("/{render_id}/download")
def download_render(render_id: int, db: Session = Depends(get_db)):
    render = db.get(Render, render_id)
    if not render or not render.output_video_path:
        raise HTTPException(status_code=404, detail="video not ready")
    return FileResponse(render.output_video_path, media_type="video/mp4", filename="output.mp4")


@router.get("/{render_id}/detail")
def get_render_detail(render_id: int, db: Session = Depends(get_db)):
    render = db.get(Render, render_id)
    if not render:
        raise HTTPException(status_code=404, detail="render not found")
    base = Path(__file__).resolve().parents[1] / "storage" / "renders" / f"{render_id}"
    status_path = base / "status.json"
    detail = {}
    if status_path.exists():
        detail = json.loads(status_path.read_text(encoding="utf-8"))
    return {
        "status": render.status,
        "progress": render.progress,
        "detail": detail,
        "output_video_path": render.output_video_path,
    }

