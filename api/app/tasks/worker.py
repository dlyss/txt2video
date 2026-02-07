from __future__ import annotations

from pathlib import Path
import json
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Render, Dialogue, ProjectSettings, Shot
from ..services.tts import synthesize_dialogues
from ..services.audio import concat_wavs
from ..services.subtitles import write_srt
from .compose import compose_video, concat_videos, burn_subtitles
from ..services.heygen import create_video, wait_for_video, download_video, create_avatar_iv_video
from ..settings import settings


def render_job(render_id: int) -> None:
    db: Session = SessionLocal()
    try:
        render = db.get(Render, render_id)
        if not render:
            return

        render.status = "processing"
        render.progress = 5
        db.commit()

        dialogues = db.query(Dialogue).filter(Dialogue.project_id == render.project_id).all()
        if not dialogues:
            render.status = "failed"
            render.progress = 0
            db.commit()
            return

        output_dir = Path(__file__).resolve().parents[1] / "storage" / "renders" / f"{render_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        def write_status(extra: dict) -> None:
            status_path = output_dir / "status.json"
            status_path.write_text(json.dumps(extra, ensure_ascii=False), encoding="utf-8")

        render.progress = 15
        db.commit()
        write_status({"phase": "tts", "progress": render.progress})

        dialogue_dicts = [{"speaker": d.speaker, "text": d.text} for d in dialogues]
        tts_results = synthesize_dialogues(dialogue_dicts, output_dir / "tts")

        render.progress = 45
        db.commit()
        write_status({"phase": "tts_done", "progress": render.progress})

        audio_paths = [r.path for r in tts_results]
        durations = [r.duration_sec for r in tts_results]
        merged_audio = output_dir / "merged.wav"
        total_duration = concat_wavs(audio_paths, merged_audio)

        render.progress = 65
        db.commit()
        write_status({"phase": "subtitles", "progress": render.progress})

        srt_path = output_dir / "subtitles.srt"
        write_srt(dialogue_dicts, durations, srt_path)

        render.progress = 80
        db.commit()
        write_status({"phase": "compose", "progress": render.progress})

        output_path = output_dir / "output.mp4"

        heygen_ok = False
        settings_row = db.query(ProjectSettings).filter(ProjectSettings.project_id == render.project_id).first()
        bg_color_map = {
            "paper": "#f4f1ea",
            "mint": "#e7f3ef",
            "sky": "#e8f0ff",
            "sunset": "#fff1e1",
        }
        bg_color = bg_color_map.get((settings_row.background_style if settings_row else None) or "paper", "#f4f1ea")

        if settings_row and settings_row.avatar_iv_image_key and settings_row.voice_id and settings.heygen_api_key:
            try:
                clips_dir = output_dir / "iv_clips"
                clips_dir.mkdir(parents=True, exist_ok=True)
                clip_paths: list[Path] = []
                segments = []
                use_shots = bool(settings_row.use_shots_for_avatar_iv)
                if use_shots:
                    shots = db.query(Shot).filter(Shot.project_id == render.project_id).order_by(Shot.shot_index).all()
                    if shots:
                        for i, shot in enumerate(shots):
                            text = dialogue_dicts[i]["text"] if i < len(dialogue_dicts) else shot.description
                            segments.append({"text": text})
                if not segments:
                    segments = dialogue_dicts

                total = max(len(segments), 1)
                for idx, item in enumerate(segments, start=1):
                    text = item.get("text") or ""
                    if not text.strip():
                        continue
                    video_id = create_avatar_iv_video(
                        settings_row.avatar_iv_image_key,
                        text,
                        settings_row.voice_id,
                        f"p{render.project_id}-r{render_id}-c{idx}",
                    )
                    video_url = wait_for_video(video_id)
                    clip_path = clips_dir / f"clip_{idx:03d}.mp4"
                    download_video(video_url, clip_path)
                    clip_paths.append(clip_path)
                    render.progress = 80 + int(20 * (idx / total))
                    db.commit()
                    write_status({"phase": "avatar_iv", "current": idx, "total": total, "progress": render.progress})

                if clip_paths:
                    concat_videos(clip_paths, output_path)
                    if srt_path.exists():
                        subtitled = output_dir / "output_subtitled.mp4"
                        burn_subtitles(output_path, srt_path, subtitled)
                        output_path = subtitled
                else:
                    raise RuntimeError("No Avatar IV clips generated")
                heygen_ok = True
            except Exception:
                heygen_ok = False

        if not heygen_ok:
            if (
                settings.lip_sync_provider == "heygen"
                and settings.heygen_api_key
                and (settings_row and settings_row.avatar_id)
                and "localhost" not in settings.public_base_url
                and "127.0.0.1" not in settings.public_base_url
            ):
                try:
                    audio_url = f"{settings.public_base_url}/api/assets/audio/{render_id}/merged.wav"
                    video_id = create_video(audio_url, settings_row.avatar_id)
                    video_url = wait_for_video(video_id)
                    download_video(video_url, output_path)
                    heygen_ok = True
                except Exception:
                    heygen_ok = False

        if not heygen_ok:
            compose_video(merged_audio, output_path, total_duration, srt_path, bg_color)

        render.status = "completed"
        render.progress = 100
        render.output_video_path = str(output_path)
        db.commit()
        write_status({"phase": "done", "progress": 100, "output": str(output_path)})
    finally:
        db.close()
