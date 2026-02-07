from __future__ import annotations

from pathlib import Path
import time
import requests

from ..settings import settings


HEYGEN_GENERATE_URL = "https://api.heygen.com/v2/video/generate"
HEYGEN_STATUS_URL = "https://api.heygen.com/v1/video_status.get"
HEYGEN_AVATARS_URL = "https://api.heygen.com/v2/avatars"
HEYGEN_VOICES_URL = "https://api.heygen.com/v2/voices"
HEYGEN_AVATAR_IV_URL = "https://api.heygen.com/v2/video/av4/generate"
HEYGEN_UPLOAD_URL = "https://upload.heygen.com/v1/asset"


def create_video(audio_url: str, avatar_id: str, api_key: str | None = None) -> str:
    api_key = api_key or settings.heygen_api_key
    if not api_key or not avatar_id:
        raise RuntimeError("HeyGen not configured")

    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": {"type": "audio", "audio_url": audio_url},
            }
        ],
        "dimension": {"width": 1280, "height": 720},
    }
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    resp = requests.post(HEYGEN_GENERATE_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HeyGen create failed: {resp.text}")
    data = resp.json()
    video_id = data.get("data", {}).get("video_id")
    if not video_id:
        raise RuntimeError("HeyGen missing video_id")
    return video_id


def wait_for_video(video_id: str, timeout_sec: int = 600, api_key: str | None = None) -> str:
    api_key = api_key or settings.heygen_api_key
    headers = {"X-Api-Key": api_key}
    start = time.time()
    while time.time() - start < timeout_sec:
        resp = requests.get(HEYGEN_STATUS_URL, params={"video_id": video_id}, headers=headers, timeout=15)
        if resp.status_code != 200:
            time.sleep(3)
            continue
        data = resp.json()
        status = data.get("data", {}).get("status")
        if status == "completed":
            video_url = data.get("data", {}).get("video_url")
            if video_url:
                return video_url
            raise RuntimeError("HeyGen completed but missing video_url")
        if status == "failed":
            raise RuntimeError("HeyGen failed")
        time.sleep(3)
    raise RuntimeError("HeyGen timeout")


def download_video(video_url: str, output_path: Path) -> None:
    resp = requests.get(video_url, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError("HeyGen download failed")
    output_path.write_bytes(resp.content)


def list_avatars(api_key: str | None = None) -> list[dict]:
    api_key = api_key or settings.heygen_api_key
    if not api_key:
        raise RuntimeError("HeyGen API key missing")
    headers = {"X-Api-Key": api_key}
    resp = requests.get(HEYGEN_AVATARS_URL, headers=headers, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"HeyGen avatars failed: {resp.text}")
    data = resp.json().get("data", [])
    return data


def list_voices(api_key: str | None = None) -> list[dict]:
    api_key = api_key or settings.heygen_api_key
    if not api_key:
        raise RuntimeError("HeyGen API key missing")
    headers = {"X-Api-Key": api_key}
    resp = requests.get(HEYGEN_VOICES_URL, headers=headers, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"HeyGen voices failed: {resp.text}")
    data = resp.json().get("data", [])
    return data


def upload_asset(filename: str, content: bytes, content_type: str, api_key: str | None = None) -> str:
    api_key = api_key or settings.heygen_api_key
    if not api_key:
        raise RuntimeError("HeyGen API key missing")
    headers = {"X-Api-Key": api_key}
    files = {"file": (filename, content, content_type)}
    resp = requests.post(HEYGEN_UPLOAD_URL, headers=headers, files=files, timeout=60)
    if resp.status_code != 200:
        # Fallback: some endpoints accept raw body
        headers_raw = {"X-Api-Key": api_key, "Content-Type": content_type}
        resp = requests.post(HEYGEN_UPLOAD_URL, headers=headers_raw, data=content, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"HeyGen upload failed: {resp.text}")
    data = resp.json()
    key = (
        data.get("data", {}).get("id")
        or data.get("data", {}).get("image_key")
        or data.get("id")
        or data.get("image_key")
    )
    if not key:
        raise RuntimeError("HeyGen upload missing image_key")
    return key


def create_avatar_iv_video(image_key: str, script: str, voice_id: str, title: str | None = None, api_key: str | None = None) -> str:
    api_key = api_key or settings.heygen_api_key
    if not api_key:
        raise RuntimeError("HeyGen API key missing")
    payload = {
        "title": title or "avatar-iv-video",
        "image_key": image_key,
        "script": script,
        "voice_id": voice_id,
        "aspect_ratio": "16:9",
    }
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    resp = requests.post(HEYGEN_AVATAR_IV_URL, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"HeyGen avatar-iv failed: {resp.text}")
    data = resp.json()
    video_id = data.get("data", {}).get("video_id") or data.get("data", {}).get("id")
    if not video_id:
        raise RuntimeError("HeyGen avatar-iv missing video_id")
    return video_id
