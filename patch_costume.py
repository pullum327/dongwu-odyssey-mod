#!/usr/bin/env python3
"""角色造型預設解鎖修補。"""
from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pefile
import UnityPy
from keystone import KS_ARCH_X86, KS_MODE_64, Ks
from UnityPy.helpers.UnityVersion import UnityVersion

from patch_common import GAME_ROOT, make_jmp_rel32, patch_bytes, place_text_code

STREAMING_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets"
ASSETS_DIR = STREAMING_DIR / "Assets"
GAME_DATA_AB = ASSETS_DIR / "game_data.ab"
GAME_DATA_BACKUP = ASSETS_DIR / "game_data.ab.ignite_mod.bak"
ASSET_MAP = STREAMING_DIR / "asset_map.json"
ASSET_MAP_BACKUP = ASSET_MAP.with_suffix(".json.ignite_mod.bak")

CHARACTER_ASSET = "assets/gamedata/character.json"

DEFAULT_MODEL_REPLACEMENTS: Mapping[str, str] = {
    "100004": "Al_FoxGarcia002",
    "100005": "Al_RabbitSyakuyaku002",
}

GET_OR_CREATE_COSTUME_RETURN_RVA = 0x96B590
GET_CHARACTER_COSTUMES_RETURN_RVA = 0x950EFC
SELECT_COSTUME_AUTO_UNLOCK_RVA = 0x9FEFC4
SELECT_COSTUME_UNLOCK_CHECK_RVA = 0x9FF3C8
BUY_COSTUME_REMOVE_CURRENCY_CALL_RVA = 0x8CC5BF
LIST_VALUETUPLE_ADD_WITH_RESIZE_VA = 0x181518140
LIST_VALUETUPLE_ADD_HELPER_PTR_VA = 0x184815D10
UNLOCK_CHARACTER_COSTUME_VA = 0x180A47B10
SELECT_COSTUME_DEFAULT_BRANCH_VA = 0x1809FF1D6
SELECT_COSTUME_CONTINUE_VA = 0x1809FEFD3

FALLBACK_COSTUMES: tuple[tuple[int, int], ...] = (
    (100004, 400001),  # FoxGarcia -> 月光白狐
    (100005, 500001),  # RabbitSyakuyaku -> 祥瑞玉兔
)

LANGUAGE_FILES: tuple[tuple[Path, Mapping[str, str]], ...] = (
    (
        STREAMING_DIR / "strings.json",
        {
            "ChrCostume_Buy_Button_Hint": "{0}金龙解锁",
            "ChrCostume_Buy_Title": "解锁皮肤",
            "ChrCostume_Buy_Content": "是否使用<color=#D6CBA4>{0}金龙</color>购买<color=#1FC8D5>{1}</color>?",
            "ChrCostume_Dress_Button_Hint": "替换",
            "ChrCostume_Dress_Succee_Hint": "替换装扮完成",
            "ChrCostume_Dress_Failed_Same_Hint": "已替换为该装扮",
            "ChrCostume_GoTo_Unlock_Hint": "前往解锁",
            "ChrCostume_Unlock_Hint": "已解锁",
            "ChrCostume_NoHero_Hint": "还没有此角色",
        },
    ),
    (
        STREAMING_DIR / "Languages" / "zh-Hant" / "zh-Hant.json",
        {
            "ChrCostume_Buy_Button_Hint": "{0}金龍解鎖",
            "ChrCostume_Buy_Title": "解鎖裝扮",
            "ChrCostume_Buy_Content": "是否使用<color=#D6CBA4>{0}金龍</color>購買<color=#1FC8D5>{1}</color>?",
            "ChrCostume_Dress_Button_Hint": "替換",
            "ChrCostume_Dress_Succee_Hint": "替換裝扮完成",
            "ChrCostume_Dress_Failed_Same_Hint": "已替換為該裝扮",
            "ChrCostume_GoTo_Unlock_Hint": "前往解鎖",
            "ChrCostume_Unlock_Hint": "已解鎖",
            "ChrCostume_NoHero_Hint": "還沒有此角色",
        },
    ),
    (
        STREAMING_DIR / "Languages" / "en-US" / "en-US.json",
        {
            "ChrCostume_Buy_Button_Hint": "{0} Unlock",
            "ChrCostume_Buy_Title": "Unlock",
            "ChrCostume_Buy_Content": "Do you want to use <color=#D6CBA4>{0} Golden Dragon</color> to purchase <color=#1FC8D5>{1}</color>?",
            "ChrCostume_Dress_Button_Hint": "replace",
            "ChrCostume_Dress_Succee_Hint": "Complete the costume change",
            "ChrCostume_Dress_Failed_Same_Hint": "Replaced with this outfit",
            "ChrCostume_GoTo_Unlock_Hint": "Go to Unlock",
            "ChrCostume_Unlock_Hint": "Unlocked",
            "ChrCostume_NoHero_Hint": "There is no such role yet",
        },
    ),
)


def _backup_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".ignite_mod.bak")


def _patch_unity_version_parser() -> None:
    old_from_str = UnityVersion.from_str.__func__

    def from_str(cls: type[UnityVersion], version: object) -> UnityVersion:
        text = str(version)
        if "c" in text:
            text = text.split("c", 1)[0]
        return old_from_str(cls, text)

    UnityVersion.from_str = classmethod(from_str)


def _load_text_asset_json(env: UnityPy.Environment, key: str) -> tuple[object, dict]:
    obj = env.container[key]
    tree = obj.read_typetree()
    return obj, json.loads(tree["m_Script"])


def _save_text_asset_json(obj: object, payload: dict) -> None:
    data = obj.read()
    data.m_Script = json.dumps(payload, ensure_ascii=False, separators=(",", ": "))
    data.save()


def _update_asset_map_size(bundle_size_without_prefix: int) -> None:
    if not ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP, ASSET_MAP_BACKUP)

    asset_map = json.loads(ASSET_MAP.read_text(encoding="utf-8"))
    if "size" in asset_map and "game_data.ab" in asset_map["size"]:
        asset_map["size"]["game_data.ab"] = bundle_size_without_prefix
    ASSET_MAP.write_text(json.dumps(asset_map, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def _apply_default_costume_models() -> int:
    if not GAME_DATA_AB.exists():
        raise SystemExit(f"找不到 {GAME_DATA_AB}")
    if not GAME_DATA_BACKUP.exists():
        shutil.copy2(GAME_DATA_AB, GAME_DATA_BACKUP)
        print(f"  [backup] {GAME_DATA_BACKUP.name}")

    raw = GAME_DATA_AB.read_bytes()
    if raw[:8] != b"OGODJ\x01\x00\x00":
        raise SystemExit("game_data.ab header 不符合預期，停止修補")

    _patch_unity_version_parser()
    env = UnityPy.load(raw[8:])
    character_obj, characters = _load_text_asset_json(env, CHARACTER_ASSET)

    changed = 0
    for character_id, model in DEFAULT_MODEL_REPLACEMENTS.items():
        character = characters.get(character_id)
        if character is None:
            raise SystemExit(f"找不到 Character id={character_id}")
        if character.get("model") != model:
            character["model"] = model
            changed += 1

    if changed:
        _save_text_asset_json(character_obj, characters)
        saved = env.file.save()
        GAME_DATA_AB.write_bytes(raw[:8] + saved)
        _update_asset_map_size(len(saved))

    return changed


def _replace_keys(payload: Any, replacements: Mapping[str, str]) -> int:
    changed = 0
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in replacements and value != replacements[key]:
                payload[key] = replacements[key]
                changed += 1
            else:
                changed += _replace_keys(value, replacements)
    elif isinstance(payload, list):
        for item in payload:
            changed += _replace_keys(item, replacements)
    return changed


def _restore_costume_texts() -> int:
    total = 0
    for path, replacements in LANGUAGE_FILES:
        if not path.exists():
            continue

        backup = _backup_path(path)
        if not backup.exists():
            shutil.copy2(path, backup)

        payload = json.loads(path.read_text(encoding="utf-8"))
        changed = _replace_keys(payload, replacements)
        if changed:
            path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            total += changed

    return total


def _build_unlock_return_stub() -> bytes:
    asm = """
        mov rbp, [rsp+0x30]
        mov [rbx+0x20], rdi
        mov rdx, [rbx+0x18]
        test rdx, rdx
        je finish
        mov r8d, [rdx+0x18]
        mov rdx, [rdx+0x10]
        test rdx, rdx
        je finish
        xor r9d, r9d
    loop_items:
        cmp r9d, r8d
        jge finish
        mov rax, [rdx+r9*8+0x20]
        test rax, rax
        je next_item
        mov byte ptr [rax+0x20], 1
    next_item:
        inc r9d
        jmp loop_items
    finish:
        mov rax, rbx
        mov rsi, [rsp+0x40]
        mov rbx, [rsp+0x38]
        add rsp, 0x20
        pop rdi
        ret
    """
    ks = Ks(KS_ARCH_X86, KS_MODE_64)
    encoded, _count = ks.asm(asm)
    return bytes(encoded)


def _build_select_auto_unlock_stub() -> bytes:
    asm = f"""
        cmp qword ptr [rsp+0xe8], 0
        jle default_costume
        mov rcx, r15
        mov rdx, [rsp+0xe8]
        mov r8, [rbx+0x10]
        mov rax, 0x{UNLOCK_CHARACTER_COSTUME_VA:X}
        call rax
        mov rax, 0x{SELECT_COSTUME_CONTINUE_VA:X}
        jmp rax
    default_costume:
        mov rax, 0x{SELECT_COSTUME_DEFAULT_BRANCH_VA:X}
        jmp rax
    """
    ks = Ks(KS_ARCH_X86, KS_MODE_64)
    encoded, _count = ks.asm(asm)
    return bytes(encoded)


def _build_get_character_costumes_stub() -> bytes:
    checks: list[str] = []
    for idx, (character_id, costume_id) in enumerate(FALLBACK_COSTUMES):
        checks.append(
            f"""
            cmp rsi, {character_id}
            je costume_{idx}
            """
        )

    cases: list[str] = []
    for idx, (_character_id, costume_id) in enumerate(FALLBACK_COSTUMES):
        cases.append(
            f"""
            costume_{idx}:
                mov eax, {costume_id}
                jmp add_costume
            """
        )

    asm = f"""
        test rdi, rdi
        je finish
        cmp dword ptr [rdi+0x18], 0
        jne finish
        {"".join(checks)}
        jmp finish
        {"".join(cases)}
    add_costume:
        mov qword ptr [rsp+0x40], rax
        mov qword ptr [rsp+0x48], 1
        movabs r8, 0x{LIST_VALUETUPLE_ADD_HELPER_PTR_VA:X}
        mov r8, [r8]
        lea rdx, [rsp+0x40]
        mov rcx, rdi
        movabs rax, 0x{LIST_VALUETUPLE_ADD_WITH_RESIZE_VA:X}
        call rax
    finish:
        mov rax, rdi
        lea r11, [rsp+0x90]
        mov rbx, [r11+0x18]
        mov rsi, [r11+0x20]
        mov rsp, r11
        pop rdi
        ret
    """
    ks = Ks(KS_ARCH_X86, KS_MODE_64)
    encoded, _count = ks.asm(asm)
    return bytes(encoded)


def apply_costume_unlock(pe: pefile.PE, data: bytearray) -> None:
    from game_data import GameDataSession
    from mods.costume_defs import apply_costume_default_models

    session = GameDataSession()
    apply_costume_default_models(session)
    session.save()
    _restore_costume_texts()


def restore_costume_texts() -> None:
    restored = 0
    for path, _replacements in LANGUAGE_FILES:
        backup = _backup_path(path)
        if backup.exists():
            shutil.copy2(backup, path)
            restored += 1

    if restored:
        print(f"已還原角色造型文案: {restored} 個檔案")
