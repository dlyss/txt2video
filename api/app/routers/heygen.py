from __future__ import annotations

from fastapi import APIRouter, HTTPException
from ..services.heygen import list_avatars, list_voices

router = APIRouter(prefix="/api/heygen", tags=["heygen"])


@router.get("/avatars")
def get_avatars():
    try:
        return {"data": list_avatars()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/voices")
def get_voices():
    try:
        return {"data": list_voices()}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

