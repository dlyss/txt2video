from __future__ import annotations

from typing import Dict, List


def generate_storyboard(parsed_json: Dict) -> List[Dict]:
    shots: List[Dict] = []
    shot_index = 1
    for scene in parsed_json.get("scenes", []):
        for item in scene.get("dialogue", []):
            description = f"{item.get('speaker', '角色')} 对话：{item.get('text', '')}"
            shots.append(
                {
                    "shot_index": shot_index,
                    "description": description,
                    "duration_sec": 3,
                }
            )
            shot_index += 1
    return shots


