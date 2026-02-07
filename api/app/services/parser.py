from __future__ import annotations

from typing import Dict, List


def parse_script(raw_text: str) -> Dict:
    # Very simple parser: split by lines, treat "角色: 台词" as dialogue
    scenes: List[Dict] = []
    current_scene = {"scene_id": 1, "location": "未指定", "characters": [], "dialogue": []}

    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            # Scene title
            if current_scene["dialogue"]:
                scenes.append(current_scene)
                current_scene = {
                    "scene_id": len(scenes) + 1,
                    "location": line.lstrip("# "),
                    "characters": [],
                    "dialogue": [],
                }
            else:
                current_scene["location"] = line.lstrip("# ")
            continue
        if ":" in line:
            speaker, text = line.split(":", 1)
            speaker = speaker.strip()
            text = text.strip()
            if speaker and text:
                if speaker not in current_scene["characters"]:
                    current_scene["characters"].append(speaker)
                current_scene["dialogue"].append({"speaker": speaker, "text": text})
        else:
            # fallback as narration
            current_scene["dialogue"].append({"speaker": "旁白", "text": line})
            if "旁白" not in current_scene["characters"]:
                current_scene["characters"].append("旁白")

    if current_scene["dialogue"]:
        scenes.append(current_scene)

    return {"scenes": scenes}


