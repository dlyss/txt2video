from __future__ import annotations

from fastapi import APIRouter, HTTPException
from ..services.heygen import list_avatars, list_voices
from ..models import SystemSettings
from ..services.crypto import decrypt
from ..db import SessionLocal

router = APIRouter(prefix="/api/heygen", tags=["heygen"])


@router.get("/avatars")
def get_avatars():
    db = SessionLocal()
    try:
        row = db.query(SystemSettings).first()
        api_key = decrypt(row.heygen_api_key_enc or "") if row else ""
        return {"data": list_avatars(api_key=api_key or None)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        db.close()


@router.get("/voices")
def get_voices():
    db = SessionLocal()
    try:
        row = db.query(SystemSettings).first()
        api_key = decrypt(row.heygen_api_key_enc or "") if row else ""
        return {"data": list_voices(api_key=api_key or None)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        db.close()
