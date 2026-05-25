#!/usr/bin/env python3
"""依 mods_enabled.json 選擇性套用 Mod（需先關閉遊戲）。

用法：
  python apply_mods.py              # 依 mods_enabled.json 套用
  python apply_mods.py --list       # 列出所有 mod
  python apply_mods.py --only ignite_no_consume,enemy_hp_multiplier
  python apply_mods.py --enable polish_soul_siphon --disable gacha_xijin_pool
  python apply_mods.py --restore    # 還原 DLL 與 game_data.ab
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import pefile

from game_data import restore_game_data_from_backup
from mod_registry import ALL_MODS, DEFAULT_ENABLED, MOD_BY_ID, STRING_MODS
from patch_common import DLL, sha256, write_dll
from patch_costume import restore_costume_texts
from patch_gacha import restore_gacha_data

ROOT = Path(__file__).resolve().parent
GAME_ROOT = ROOT.parent
BACKUP = GAME_ROOT / "GameAssembly.dll.ignite_mod.bak"
ENABLED_PATH = ROOT / "mods_enabled.json"


def load_enabled_config() -> dict[str, bool]:
    if ENABLED_PATH.exists():
        data = json.loads(ENABLED_PATH.read_text(encoding="utf-8"))
        enabled = dict(DEFAULT_ENABLED)
        enabled.update({k: bool(v) for k, v in data.items()})
        return enabled
    return dict(DEFAULT_ENABLED)


def save_enabled_config(enabled: dict[str, bool]) -> None:
    payload = {mod.id: enabled.get(mod.id, False) for mod in ALL_MODS}
    ENABLED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="選擇性套用東吳大冒險 Mod")
    parser.add_argument("--restore", action="store_true", help="還原備份")
    parser.add_argument("--list", action="store_true", help="列出所有 mod")
    parser.add_argument("--only", metavar="IDS", help="只套用指定 mod（逗號分隔，不寫入設定）")
    parser.add_argument("--save", action="store_true", help="將 --only / --enable / --disable 寫入 mods_enabled.json")
    parser.add_argument("--enable", metavar="IDS", help="啟用 mod 並寫入設定")
    parser.add_argument("--disable", metavar="IDS", help="停用 mod 並寫入設定")
    return parser.parse_args(argv)


def resolve_enabled(args: argparse.Namespace) -> dict[str, bool]:
    enabled = load_enabled_config()

    if args.enable:
        for mod_id in _split_ids(args.enable):
            if mod_id not in MOD_BY_ID:
                raise SystemExit(f"未知 mod: {mod_id}")
            enabled[mod_id] = True

    if args.disable:
        for mod_id in _split_ids(args.disable):
            if mod_id not in MOD_BY_ID:
                raise SystemExit(f"未知 mod: {mod_id}")
            enabled[mod_id] = False

    if args.only:
        only = set(_split_ids(args.only))
        unknown = only - MOD_BY_ID.keys()
        if unknown:
            raise SystemExit(f"未知 mod: {', '.join(sorted(unknown))}")
        enabled = {mod_id: mod_id in only for mod_id in MOD_BY_ID}

    if args.enable or args.disable or (args.only and args.save):
        save_enabled_config(enabled)

    return enabled


def _split_ids(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def print_mod_list(enabled: dict[str, bool]) -> None:
    current_category = ""
    for mod in ALL_MODS:
        if mod.category != current_category:
            current_category = mod.category
            print(f"\n[{current_category}]")
        flag = "ON " if enabled.get(mod.id) else "OFF"
        print(f"  {flag}  {mod.id:<28} {mod.name}")


def restore_all() -> None:
    if not BACKUP.exists():
        raise SystemExit(f"沒有備份 {BACKUP}")
    shutil.copy2(BACKUP, DLL)
    restore_gacha_data()
    restore_costume_texts()
    restore_game_data_from_backup()
    print(f"已還原 {DLL} 與 game_data.ab")


def apply_enabled_mods(enabled: dict[str, bool]) -> None:
    active = [mod for mod in ALL_MODS if enabled.get(mod.id)]
    if not active:
        print("沒有啟用任何 mod。")
        return

    dll_mods = [m for m in active if m.kind == "dll"]
    data_mods = [m for m in active if m.kind == "game_data"]

    if dll_mods:
        if not DLL.exists():
            raise SystemExit(f"找不到 {DLL}")
        if not BACKUP.exists():
            shutil.copy2(DLL, BACKUP)
            print(f"已建立備份: {BACKUP}")

        pe = pefile.PE(str(BACKUP))
        data = bytearray(BACKUP.read_bytes())
        backup_bytes = bytes(BACKUP.read_bytes())
        print(f"\n修補前 SHA256（備份）: {sha256(BACKUP)}")

        for mod in dll_mods:
            print(f"=== {mod.category} / {mod.name} ===")
            mod.apply(pe, data, backup_bytes)

        write_dll(data, BACKUP)

    if data_mods:
        from game_data import GameDataSession

        print("\n=== game_data.ab ===")
        session = GameDataSession()
        for mod in data_mods:
            print(f"--- {mod.category} / {mod.name} ---")
            mod.apply(session)
        session.save()
        print("  [ok]   game_data.ab 已寫入")

    for mod in active:
        string_apply = STRING_MODS.get(mod.id)
        if string_apply:
            print(f"--- 文案 / {mod.name} ---")
            string_apply()

    print("\n完成。請重啟遊戲後測試。")
    if dll_mods:
        print("若寫入失敗，請關閉遊戲後將 GameAssembly.dll.patched 覆蓋為 GameAssembly.dll")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    enabled = resolve_enabled(args)

    if args.list:
        print_mod_list(enabled)
        return

    if args.restore:
        restore_all()
        return

    print_mod_list(enabled)
    apply_enabled_mods(enabled)


if __name__ == "__main__":
    main()
