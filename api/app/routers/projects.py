from __future__ import annotations

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pathlib import Path
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Project, Script, Dialogue, Shot, Render, ProjectSettings
from ..schemas import (
    ProjectCreate,
    ProjectOut,
    DialogueUpdate,
    DialogueOut,
    ShotOut,
    RenderOut,
    ProjectSettingsOut,
    ProjectSettingsUpdate,
)
from ..services.parser import parse_script
from ..services.heygen import upload_asset
from ..services.storyboard import generate_storyboard
from ..tasks.queue import enqueue_render

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(title=payload.title)
    db.add(project)
    db.flush()

    script = Script(project_id=project.id, raw_text=payload.raw_text)
    db.add(script)
    db.commit()
    db.refresh(project)

    return ProjectOut(id=project.id, title=project.title)


@router.post("/{project_id}/parse")
def parse_project_script(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or not project.script:
        raise HTTPException(status_code=404, detail="project not found")

    parsed = parse_script(project.script.raw_text)
    project.script.parsed_json = json.dumps(parsed, ensure_ascii=False)
    db.commit()

    db.query(Dialogue).filter(Dialogue.project_id == project_id).delete()
    for scene in parsed.get("scenes", []):
        for item in scene.get("dialogue", []):
            speaker = item.get("speaker", "旁白")
            text = item.get("text", "")
            if text.strip():
                db.add(Dialogue(project_id=project_id, speaker=speaker, text=text))
    db.commit()

    return parsed


@router.post("/{project_id}/storyboard", response_model=List[ShotOut])
def generate_project_storyboard(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or not project.script or not project.script.parsed_json:
        raise HTTPException(status_code=404, detail="parsed script not found")

    parsed = json.loads(project.script.parsed_json)
    shots = generate_storyboard(parsed)

    db.query(Shot).filter(Shot.project_id == project_id).delete()
    for shot in shots:
        db.add(
            Shot(
                project_id=project_id,
                shot_index=shot["shot_index"],
                description=shot["description"],
                duration_sec=shot["duration_sec"],
            )
        )
    db.commit()

    db_shots = db.query(Shot).filter(Shot.project_id == project_id).order_by(Shot.shot_index).all()
    return [
        ShotOut(
            shot_id=s.id,
            shot_index=s.shot_index,
            description=s.description,
            duration_sec=s.duration_sec,
        )
        for s in db_shots
    ]


@router.put("/{project_id}/dialogues", response_model=List[DialogueOut])
def update_dialogues(project_id: int, payload: DialogueUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    db.query(Dialogue).filter(Dialogue.project_id == project_id).delete()
    for item in payload.dialogues:
        db.add(Dialogue(project_id=project_id, speaker=item.speaker, text=item.text))
    db.commit()

    db_dialogues = db.query(Dialogue).filter(Dialogue.project_id == project_id).all()
    return [
        DialogueOut(id=d.id, speaker=d.speaker, text=d.text, audio_path=d.audio_path)
        for d in db_dialogues
    ]


@router.get("/{project_id}/dialogues", response_model=List[DialogueOut])
def get_dialogues(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    db_dialogues = db.query(Dialogue).filter(Dialogue.project_id == project_id).all()
    return [
        DialogueOut(id=d.id, speaker=d.speaker, text=d.text, audio_path=d.audio_path)
        for d in db_dialogues
    ]


@router.post("/{project_id}/render", response_model=RenderOut)
def render_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")

    render = Render(project_id=project_id, status="queued", progress=0)
    db.add(render)
    db.commit()
    db.refresh(render)

    enqueue_render(render.id)

    return RenderOut(render_id=render.id)


@router.get("/{project_id}/settings", response_model=ProjectSettingsOut)
def get_project_settings(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    settings = db.query(ProjectSettings).filter(ProjectSettings.project_id == project_id).first()
    avatar_image_url = None
    if settings and settings.avatar_image_path:
        avatar_image_url = f"/api/assets/avatar/{project_id}"
    return ProjectSettingsOut(
        avatar_id=settings.avatar_id if settings else None,
        voice_id=settings.voice_id if settings else None,
        avatar_image_url=avatar_image_url,
        avatar_iv_image_key=settings.avatar_iv_image_key if settings else None,
        background_style=settings.background_style if settings else None,
        use_shots_for_avatar_iv=bool(settings.use_shots_for_avatar_iv) if settings else True,
    )


@router.put("/{project_id}/settings", response_model=ProjectSettingsOut)
def update_project_settings(project_id: int, payload: ProjectSettingsUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    settings = db.query(ProjectSettings).filter(ProjectSettings.project_id == project_id).first()
    if not settings:
        settings = ProjectSettings(project_id=project_id)
        db.add(settings)
    if payload.avatar_id is not None:
        settings.avatar_id = payload.avatar_id
    if payload.voice_id is not None:
        settings.voice_id = payload.voice_id
    if payload.avatar_iv_image_key is not None:
        settings.avatar_iv_image_key = payload.avatar_iv_image_key
    if payload.background_style is not None:
        settings.background_style = payload.background_style
    if payload.use_shots_for_avatar_iv is not None:
        settings.use_shots_for_avatar_iv = 1 if payload.use_shots_for_avatar_iv else 0
    db.commit()
    avatar_image_url = f"/api/assets/avatar/{project_id}" if settings.avatar_image_path else None
    return ProjectSettingsOut(
        avatar_id=settings.avatar_id,
        voice_id=settings.voice_id,
        avatar_image_url=avatar_image_url,
        avatar_iv_image_key=settings.avatar_iv_image_key,
        background_style=settings.background_style,
        use_shots_for_avatar_iv=bool(settings.use_shots_for_avatar_iv),
    )


@router.post("/{project_id}/avatar")
def upload_avatar(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    settings = db.query(ProjectSettings).filter(ProjectSettings.project_id == project_id).first()
    if not settings:
        settings = ProjectSettings(project_id=project_id)
        db.add(settings)

    suffix = Path(file.filename).suffix or ".png"
    storage_dir = Path(__file__).resolve().parents[1] / "storage" / "avatars"
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / f"project_{project_id}{suffix}"
    content = file.file.read()
    target.write_bytes(content)
    settings.avatar_image_path = str(target)
    db.commit()
    return {"ok": True}


@router.post("/{project_id}/avatar-iv/upload")
def upload_avatar_iv_image(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    settings = db.query(ProjectSettings).filter(ProjectSettings.project_id == project_id).first()
    if not settings:
        settings = ProjectSettings(project_id=project_id)
        db.add(settings)

    content = file.file.read()
    image_key = upload_asset(file.filename, content, file.content_type or "image/jpeg")
    settings.avatar_iv_image_key = image_key

    suffix = Path(file.filename).suffix or ".png"
    storage_dir = Path(__file__).resolve().parents[1] / "storage" / "avatars"
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / f"project_{project_id}{suffix}"
    target.write_bytes(content)
    settings.avatar_image_path = str(target)
    db.commit()
    return {"image_key": image_key}
