from __future__ import annotations

from pathlib import Path
from typing import List


def format_ts(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    total_seconds = int(seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(dialogues: List[dict], durations: List[float], output_path: Path) -> None:
    # dialogues and durations are aligned by index
    lines = []
    current = 0.0
    for i, (d, dur) in enumerate(zip(dialogues, durations), start=1):
        start = current
        end = current + dur
        text = f"{d.get('speaker', '')}: {d.get('text', '')}".strip()
        lines.append(str(i))
        lines.append(f"{format_ts(start)} --> {format_ts(end)}")
        lines.append(text)
        lines.append("")
        current = end

    output_path.write_text("\n".join(lines), encoding="utf-8")


