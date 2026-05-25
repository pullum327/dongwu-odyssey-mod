"""Shared game_data.ab read/write session for composable data mods."""
from __future__ import annotations

import json
import shutil
from typing import Any

import UnityPy
from UnityPy.helpers.UnityVersion import UnityVersion

from patch_common import GAME_ROOT

ASSETS_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets" / "Assets"
STREAMING_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets"
GAME_DATA_AB = ASSETS_DIR / "game_data.ab"
GAME_DATA_BACKUP = ASSETS_DIR / "game_data.ab.ignite_mod.bak"
ASSET_MAP = STREAMING_DIR / "asset_map.json"
ASSET_MAP_BACKUP = ASSET_MAP.with_suffix(".json.ignite_mod.bak")
HEADER = b"OGODJ\x01\x00\x00"


def patch_unity_version_parser() -> None:
    old_from_str = UnityVersion.from_str.__func__

    def from_str(cls: type[UnityVersion], version: object) -> UnityVersion:
        text = str(version)
        if "c" in text:
            text = text.split("c", 1)[0]
        return old_from_str(cls, text)

    UnityVersion.from_str = classmethod(from_str)


def ensure_game_data_backup() -> None:
    if not GAME_DATA_AB.exists():
        raise SystemExit(f"找不到 {GAME_DATA_AB}")
    if not GAME_DATA_BACKUP.exists():
        shutil.copy2(GAME_DATA_AB, GAME_DATA_BACKUP)
        print(f"  [backup] {GAME_DATA_BACKUP.name}")


def restore_game_data_from_backup() -> None:
    if not GAME_DATA_BACKUP.exists():
        raise SystemExit(f"找不到 {GAME_DATA_BACKUP}，無法還原 game_data.ab")
    shutil.copy2(GAME_DATA_BACKUP, GAME_DATA_AB)
    if ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP_BACKUP, ASSET_MAP)


class GameDataSession:
    """Load game_data.ab once, apply multiple data mods, save once."""

    def __init__(self) -> None:
        ensure_game_data_backup()
        self._raw_header = HEADER
        self._raw_payload = GAME_DATA_BACKUP.read_bytes()[8:]
        patch_unity_version_parser()
        self.env = UnityPy.load(self._raw_payload)
        self._json_cache: dict[str, tuple[Any, dict]] = {}

    def json(self, asset_key: str) -> dict:
        if asset_key not in self._json_cache:
            obj = self.env.container[asset_key]
            tree = obj.read_typetree()
            self._json_cache[asset_key] = (obj, json.loads(tree["m_Script"]))
        return self._json_cache[asset_key][1]

    def save(self) -> None:
        for asset_key, (obj, payload) in self._json_cache.items():
            data = obj.read()
            data.m_Script = json.dumps(payload, ensure_ascii=False, separators=(",", ": "))
            data.save()

        saved = next(iter(self.env.files.values())).save()
        GAME_DATA_AB.write_bytes(self._raw_header + saved)
        self._update_asset_map_size(len(saved))

    def _update_asset_map_size(self, bundle_size_without_prefix: int) -> None:
        if not ASSET_MAP_BACKUP.exists():
            shutil.copy2(ASSET_MAP, ASSET_MAP_BACKUP)

        asset_map = json.loads(ASSET_MAP.read_text(encoding="utf-8"))
        if "size" in asset_map and "game_data.ab" in asset_map["size"]:
            asset_map["size"]["game_data.ab"] = bundle_size_without_prefix
        ASSET_MAP.write_text(
            json.dumps(asset_map, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
