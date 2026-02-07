from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import SystemSettings
from ..schemas import SystemSettingsOut, SystemSettingsUpdate
from ..services.crypto import encrypt, decrypt, mask
from ..services.tts import synthesize_dialogues
from ..services.heygen import list_avatars
from ..settings import settings
from pathlib import Path
import uuid

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
    aliyun_access_key_id = decrypt(row.aliyun_access_key_id_enc or "")
    aliyun_access_key_secret = decrypt(row.aliyun_access_key_secret_enc or "")
    aliyun_appkey = decrypt(row.aliyun_appkey_enc or "")
    heygen_api_key = decrypt(row.heygen_api_key_enc or "")
    volcengine_app_id = decrypt(row.volcengine_app_id_enc or "")
    volcengine_token = decrypt(row.volcengine_token_enc or "")
    volcengine_cluster = decrypt(row.volcengine_cluster_enc or "")
    return SystemSettingsOut(
        tts_provider=row.tts_provider,
        enable_heygen=bool(row.enable_heygen),
        enable_avatar_iv=bool(row.enable_avatar_iv),
        aliyun_access_key_id_masked=mask(aliyun_access_key_id),
        aliyun_access_key_secret_masked=mask(aliyun_access_key_secret),
        aliyun_appkey_masked=mask(aliyun_appkey),
        heygen_api_key_masked=mask(heygen_api_key),
        volcengine_app_id_masked=mask(volcengine_app_id),
        volcengine_token_masked=mask(volcengine_token),
        volcengine_cluster=volcengine_cluster,
        volcengine_voice_type=row.volcengine_voice_type or settings.volcengine_voice_type,
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
    if payload.aliyun_access_key_id is not None:
        row.aliyun_access_key_id_enc = encrypt(payload.aliyun_access_key_id) if payload.aliyun_access_key_id else None
    if payload.aliyun_access_key_secret is not None:
        row.aliyun_access_key_secret_enc = encrypt(payload.aliyun_access_key_secret) if payload.aliyun_access_key_secret else None
    if payload.aliyun_appkey is not None:
        row.aliyun_appkey_enc = encrypt(payload.aliyun_appkey) if payload.aliyun_appkey else None
    if payload.heygen_api_key is not None:
        row.heygen_api_key_enc = encrypt(payload.heygen_api_key) if payload.heygen_api_key else None
    if payload.volcengine_app_id is not None:
        row.volcengine_app_id_enc = encrypt(payload.volcengine_app_id) if payload.volcengine_app_id else None
    if payload.volcengine_token is not None:
        row.volcengine_token_enc = encrypt(payload.volcengine_token) if payload.volcengine_token else None
    if payload.volcengine_cluster is not None:
        row.volcengine_cluster_enc = encrypt(payload.volcengine_cluster) if payload.volcengine_cluster else None
    if payload.volcengine_voice_type is not None:
        row.volcengine_voice_type = payload.volcengine_voice_type
    db.commit()
    return get_settings(db)


@router.post("/test/tts")
def test_tts(db: Session = Depends(get_db)):
    row = _get_or_create(db)
    config = _collect_tts_config(row)
    output_dir = Path(__file__).resolve().parents[1] / "storage" / "tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex[:8]
    results = synthesize_dialogues(
        [{"speaker": "系统", "text": "这是语音合成测试"}],
        output_dir / token,
        provider=row.tts_provider,
        config=config,
    )
    return {"ok": True, "provider": row.tts_provider, "duration": results[0].duration_sec}


@router.post("/test/heygen")
def test_heygen(db: Session = Depends(get_db)):
    row = _get_or_create(db)
    if not row.enable_heygen:
        return {"ok": False, "detail": "heygen disabled"}
    api_key = decrypt(row.heygen_api_key_enc or "") or settings.heygen_api_key
    data = list_avatars(api_key=api_key)
    return {"ok": True, "avatar_count": len(data)}


def _collect_tts_config(row: SystemSettings) -> dict:
    return {
        "aliyun_access_key_id": decrypt(row.aliyun_access_key_id_enc or "") or settings.aliyun_access_key_id,
        "aliyun_access_key_secret": decrypt(row.aliyun_access_key_secret_enc or "") or settings.aliyun_access_key_secret,
        "aliyun_appkey": decrypt(row.aliyun_appkey_enc or "") or settings.aliyun_appkey,
        "volcengine_app_id": decrypt(row.volcengine_app_id_enc or "") or settings.volcengine_app_id,
        "volcengine_token": decrypt(row.volcengine_token_enc or "") or settings.volcengine_token,
        "volcengine_cluster": decrypt(row.volcengine_cluster_enc or "") or settings.volcengine_cluster,
        "volcengine_voice_type": row.volcengine_voice_type or settings.volcengine_voice_type,
    }
