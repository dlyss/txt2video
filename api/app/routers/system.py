from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import SystemSettings
from ..schemas import SystemSettingsOut, SystemSettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_create(db: Session) -> SystemSettings:
    row = db.query(SystemSettings).first()
    if not row:
        row = SystemSettings(tts_provider="aliyun", enable_heygen=1, enable_avatar_iv=1)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("", response_model=SystemSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    row = _get_or_create(db)
    return SystemSettingsOut(
        tts_provider=row.tts_provider,
        enable_heygen=bool(row.enable_heygen),
        enable_avatar_iv=bool(row.enable_avatar_iv),
    )


@router.put("", response_model=SystemSettingsOut)
def update_settings(payload: SystemSettingsUpdate, db: Session = Depends(get_db)):
    row = _get_or_create(db)
    if payload.tts_provider is not None:
        row.tts_provider = payload.tts_provider
    if payload.enable_heygen is not None:
        row.enable_heygen = 1 if payload.enable_heygen else 0
    if payload.enable_avatar_iv is not None:
        row.enable_avatar_iv = 1 if payload.enable_avatar_iv else 0
    db.commit()
    return SystemSettingsOut(
        tts_provider=row.tts_provider,
        enable_heygen=bool(row.enable_heygen),
        enable_avatar_iv=bool(row.enable_avatar_iv),
    )

