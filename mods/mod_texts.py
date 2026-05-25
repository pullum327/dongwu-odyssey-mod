"""Locale strings for custom equipment/polish effects."""
from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patch_common import GAME_ROOT

STREAMING_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets"

SHENWEI_TEXT_KEYS = {
    "EquipmentEffect_name_7599002": {
        "strings": "神威",
        "zh-Hant": "神威",
        "zh-Hans": "神威",
        "en-US": "Divine Might",
    },
    "EquipmentEffect_describe_7599002": {
        "strings": "提高反击&追击伤害和速度",
        "zh-Hant": "提高反擊&追擊傷害和速度",
        "zh-Hans": "提高反击&追击伤害和速度",
        "en-US": "Increase riposte, pursuit damage, and speed",
    },
    "EquipmentEffect_contentLv1_7599002": {
        "strings": "反击&追击伤害+<param1[0].p>，速度+<param1[2]>",
        "zh-Hant": "反擊&追擊傷害+<param1[0].p>，速度+<param1[2]>",
        "zh-Hans": "反击&追击伤害+<param1[0].p>，速度+<param1[2]>",
        "en-US": "Riposte & Pursuit Damage +<param1[0].p>, Speed +<param1[2]>",
    },
}

SOUL_SIPHON_TEXT_KEYS = {
    "EquipmentEffect_name_7599003": {
        "strings": "灵魂虹吸",
        "zh-Hant": "靈魂虹吸",
        "zh-Hans": "灵魂虹吸",
        "en-US": "Soul Siphon",
    },
    "EquipmentEffect_describe_7599003": {
        "strings": "造成伤害时恢复伤害的血量，并提高最终伤害",
        "zh-Hant": "造成傷害時回復傷害的血量，並提高最終傷害",
        "zh-Hans": "造成伤害时恢复伤害的血量，并提高最终伤害",
        "en-US": "Heal based on damage dealt and increase final damage",
    },
    "EquipmentEffect_contentLv1_7599003": {
        "strings": "造成伤害时恢复伤害的<param1[0].p>血量；最终伤害+<param1[1].p>",
        "zh-Hant": "造成傷害時回復傷害的<param1[0].p>血量；最終傷害+<param1[1].p>",
        "zh-Hans": "造成伤害时恢复伤害的<param1[0].p>血量；最终伤害+<param1[1].p>",
        "en-US": "Heal for <param1[0].p> of damage dealt; Final Damage +<param1[1].p>",
    },
}

LANGUAGE_FILES: tuple[tuple[Path, str], ...] = (
    (STREAMING_DIR / "strings.json", "strings"),
    (STREAMING_DIR / "Languages" / "zh-Hant" / "zh-Hant.json", "zh-Hant"),
    (STREAMING_DIR / "Languages" / "zh-Hans" / "zh-Hans.json", "zh-Hans"),
    (STREAMING_DIR / "Languages" / "en-US" / "en-US.json", "en-US"),
)


def _language_backup_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".ignite_mod.bak")


def _set_keys(payload: Any, replacements: Mapping[str, str]) -> int:
    changed = 0
    if isinstance(payload, dict):
        for key, value in replacements.items():
            if payload.get(key) != value:
                payload[key] = value
                changed += 1
        for value in payload.values():
            changed += _set_keys(value, replacements)
    elif isinstance(payload, list):
        for item in payload:
            changed += _set_keys(item, replacements)
    return changed


def apply_text_keys(text_keys: Mapping[str, Mapping[str, str]]) -> int:
    total = 0
    for path, locale in LANGUAGE_FILES:
        if not path.exists():
            continue

        backup = _language_backup_path(path)
        if not backup.exists():
            shutil.copy2(path, backup)

        replacements = {key: values[locale] for key, values in text_keys.items()}
        payload = json.loads(path.read_text(encoding="utf-8"))
        changed = _set_keys(payload, replacements)
        if changed:
            path.write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            total += changed
    return total


def apply_shenwei_texts() -> None:
    changed = apply_text_keys(SHENWEI_TEXT_KEYS)
    if changed:
        print(f"  [ok]   text_shenwei UI 文案 {changed} 項")


def apply_soul_siphon_texts() -> None:
    changed = apply_text_keys(SOUL_SIPHON_TEXT_KEYS)
    if changed:
        print(f"  [ok]   text_soul_siphon UI 文案 {changed} 項")
