"""Costume default model mod."""
from __future__ import annotations

from collections.abc import Mapping

from game_data import GameDataSession

CHARACTER_ASSET = "assets/gamedata/character.json"

DEFAULT_MODEL_REPLACEMENTS: Mapping[str, str] = {
    "100004": "Al_FoxGarcia002",
    "100005": "Al_RabbitSyakuyaku002",
}


def apply_costume_default_models(session: GameDataSession) -> None:
    characters = session.json(CHARACTER_ASSET)
    changed = 0
    for character_id, model in DEFAULT_MODEL_REPLACEMENTS.items():
        character = characters.get(character_id)
        if character is None:
            raise SystemExit(f"找不到 Character id={character_id}")
        if character.get("model") != model:
            character["model"] = model
            changed += 1

    print(f"  [ok]   costume_default_models {changed} 個角色預設造型")
