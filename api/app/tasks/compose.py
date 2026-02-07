from __future__ import annotations

from pathlib import Path
import subprocess


def compose_video(
    audio_path: Path,
    output_path: Path,
    duration_sec: float,
    srt_path: Path | None = None,
    background_color: str = "#f4f1ea",
) -> None:
    # Placeholder: create a solid-color background and merge audio.
    # Replace with real pipeline: lip-sync clips + subtitles.
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c={background_color}:s=1280x720:d={max(duration_sec, 1):.2f}",
        "-i",
        str(audio_path),
    ]
    if srt_path and srt_path.exists():
        cmd += ["-vf", f"subtitles={srt_path}"]

    cmd += [
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def concat_videos(input_paths: list[Path], output_path: Path) -> None:
    # Use ffmpeg concat demuxer for mp4 clips with same codec params.
    list_file = output_path.with_suffix(".txt")
    lines = [f"file '{p.as_posix()}'" for p in input_paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


def burn_subtitles(video_in: Path, srt_path: Path, output_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_in),
        "-vf",
        f"subtitles={srt_path}",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
