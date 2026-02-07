from __future__ import annotations

from pathlib import Path
import wave


SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1


def estimate_duration(text: str) -> float:
    # Rough estimate: 6 chars per second, min 1s
    length = max(len(text.strip()), 1)
    return max(length / 6.0, 1.0)


def write_silence_wav(output_path: Path, duration_sec: float) -> None:
    frames = int(SAMPLE_RATE * duration_sec)
    silence = b"\x00\x00" * frames
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(silence)


def concat_wavs(input_paths: list[Path], output_path: Path) -> float:
    total_frames = 0
    with wave.open(str(output_path), "wb") as out_wf:
        out_wf.setnchannels(CHANNELS)
        out_wf.setsampwidth(SAMPLE_WIDTH)
        out_wf.setframerate(SAMPLE_RATE)
        for p in input_paths:
            with wave.open(str(p), "rb") as in_wf:
                frames = in_wf.readframes(in_wf.getnframes())
                total_frames += in_wf.getnframes()
                out_wf.writeframes(frames)
    return total_frames / SAMPLE_RATE


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
    return frames / float(rate)

