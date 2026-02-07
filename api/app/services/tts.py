from __future__ import annotations

from pathlib import Path
from typing import List
import time
import json
import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import base64

from .audio import estimate_duration, write_silence_wav, wav_duration
from ..settings import settings


class TTSLineResult:
    def __init__(self, path: Path, duration_sec: float) -> None:
        self.path = path
        self.duration_sec = duration_sec


_token_cache = {"token": "", "expire_at": 0.0}


def _get_aliyun_token() -> str:
    if _token_cache["token"] and _token_cache["expire_at"] > time.time() + 60:
        return _token_cache["token"]

    if not settings.aliyun_access_key_id or not settings.aliyun_access_key_secret:
        return ""

    client = AcsClient(
        settings.aliyun_access_key_id,
        settings.aliyun_access_key_secret,
        settings.aliyun_region,
    )
    request = CommonRequest()
    request.set_method("POST")
    request.set_domain("nlsmeta.ap-southeast-1.aliyuncs.com")
    request.set_version("2019-07-17")
    request.set_action_name("CreateToken")

    response = client.do_action_with_exception(request)
    data = json.loads(response.decode("utf-8"))
    token = data.get("Token", {}).get("Id", "")
    expire = data.get("Token", {}).get("ExpireTime", 0)
    if token:
        _token_cache["token"] = token
        _token_cache["expire_at"] = float(expire)
    return token


def _aliyun_tts(text: str, output_path: Path) -> float:
    token = _get_aliyun_token()
    if not token or not settings.aliyun_appkey:
        raise RuntimeError("Aliyun TTS not configured")

    url = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/tts"
    payload = {
        "appkey": settings.aliyun_appkey,
        "token": token,
        "text": text,
        "format": "wav",
        "sample_rate": 16000,
        "voice": "xiaoyun",
        "volume": 50,
        "speech_rate": 0,
        "pitch_rate": 0,
    }
    headers = {"Content-Type": "application/json", "X-NLS-Token": token}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    if resp.status_code != 200 or resp.headers.get("Content-Type", "").startswith("application/json"):
        raise RuntimeError(f"Aliyun TTS failed: {resp.text}")
    output_path.write_bytes(resp.content)
    return wav_duration(output_path)


def _volcengine_tts(text: str, output_path: Path) -> float:
    if not settings.volcengine_app_id or not settings.volcengine_token or not settings.volcengine_cluster:
        raise RuntimeError("Volcengine TTS not configured")

    url = "https://openspeech.bytedance.com/api/v1/tts"
    payload = {
        "app": {
            "appid": settings.volcengine_app_id,
            "token": settings.volcengine_token,
            "cluster": settings.volcengine_cluster,
        },
        "user": {"uid": "txt2video"},
        "audio": {
            "voice_type": settings.volcengine_voice_type,
            "encoding": "wav",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {"text": text, "reqid": str(int(time.time() * 1000)), "text_type": "plain"},
    }
    headers = {"Authorization": f"Bearer; {settings.volcengine_token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Volcengine TTS failed: {resp.text}")

    content_type = resp.headers.get("Content-Type", "")
    if content_type.startswith("audio/") or content_type == "application/octet-stream":
        output_path.write_bytes(resp.content)
        return wav_duration(output_path)

    data = resp.json()
    audio_b64 = data.get("data") or data.get("audio") or data.get("data_base64")
    if not audio_b64:
        raise RuntimeError("Volcengine TTS missing audio data")
    output_path.write_bytes(base64.b64decode(audio_b64))
    return wav_duration(output_path)

def synthesize_dialogues(
    dialogues: List[dict],
    output_dir: Path,
    provider: str | None = None,
) -> List[TTSLineResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results: List[TTSLineResult] = []
    use_provider = provider or settings.tts_provider

    for idx, d in enumerate(dialogues, start=1):
        text = d.get("text", "")
        out_path = output_dir / f"line_{idx:03d}.wav"
        try:
            if use_provider == "aliyun":
                duration = _aliyun_tts(text, out_path)
            elif use_provider == "volcengine":
                duration = _volcengine_tts(text, out_path)
            else:
                duration = estimate_duration(text)
                write_silence_wav(out_path, duration)
        except Exception:
            duration = estimate_duration(text)
            write_silence_wav(out_path, duration)
        results.append(TTSLineResult(out_path, duration))

    return results
