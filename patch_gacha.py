#!/usr/bin/env python3
"""希金爺交易會（卡池 ID 4）資料層權重修補。

池 4 的 GachaPool.gachaName 是 "new1"，所以直接修改 game_data.ab 內的
GachaItemTabnew1.json：Rare 3/4 保留權重，其他 Rare 權重歸零。
這比在 GameAssembly.dll 內重抽穩定，因為不會重跑抽卡流程或改動暫存器。
"""
from __future__ import annotations

import json
import shutil
import struct
from pathlib import Path

import pefile
import UnityPy
from UnityPy.helpers.UnityVersion import UnityVersion

from patch_common import (
    GAME_ROOT,
)

POOL_SAVE_HOOK_RVA = 0x93E996
POOL_SAVE_HOOK_LEN = 6
POOL_SAVE_CONTINUE_RVA = 0x93E99C

# test rdi, rdi（0x93ED74 已 mov rdi,rax = GachaItemData）
POST_GET_ITEM_HOOK_RVA = 0x93ED90
POST_GET_ITEM_HOOK_LEN = 9
POST_GET_ITEM_NULL_RVA = 0x93EFE3
POST_GET_ITEM_CONTINUE_RVA = 0x93ED99

RETRY_RVA = 0x93ED50

GACHA_POOL_XIJIN = 4
EPIC_RARE_A = 3
EPIC_RARE_B = 4
MAX_RETRIES = 128

# 使用者指定補入常駐希金池的限定史詩裝備道具 ID。
XIJIN_EXTRA_EPIC_ITEMS: dict[int, str] = {
    41430013: "巨蜥骨飾",
    41430008: "名伶殘羽",
    41420017: "索羅輕甲",
    41430003: "大世界法典",
    41430021: "蠻野口籠",
}

XIJIN_REMOVED_EPIC_ITEMS: dict[int, str] = {
    41410007: "棘刺弓",
    41420014: "大鱉骨甲",
    41420003: "納塔維爾鱗甲",
    41420002: "商會鏽金長袍",
    41410004: "無畏利爪",
    41410002: "將軍佩劍",
    41410011: "墮落鐵鏈",
    41420004: "倪卡科之護",
    41420012: "疣豬泥肩甲",
    41420005: "北境戍寒甲",
    41410014: "毒懶鉤爪",
    41410005: "荒野骨棒",
    41410003: "鬥士暗金拳刃",
    41410015: "石中刺",
    41410010: "白光",
    41420013: "銀鈴花禁衛甲胄",
    41410013: "疾雷",
    41420010: "隊長板甲",
    41420011: "浦勞貴族鎖甲",
    41420015: "梅花蠻繡衣",
    41430010: "箭翎皮帽",
    41430015: "荊棘血果",
    41430025: "龍爪戒",
}

ASSETS_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets" / "Assets"
GAME_DATA_AB = ASSETS_DIR / "game_data.ab"
GAME_DATA_BACKUP = ASSETS_DIR / "game_data.ab.ignite_mod.bak"
ASSET_MAP = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets" / "asset_map.json"
ASSET_MAP_BACKUP = ASSET_MAP.with_suffix(".json.ignite_mod.bak")

GACHA_POOL_ASSET = "assets/gamedata/gachapool.json"
GACHA_ITEM_ASSET_PREFIX = "assets/gamedata/gachaitemtab"


def build_pool_save_stub(cave_rva: int, pool_slot_rva: int) -> bytes:
    """記錄 pool id，保留原本 cmp 初始化檢查由 0x93E99C 繼續執行。"""
    stub = bytearray()
    stub += b"\x48\x8B\xDA"  # mov rbx, rdx
    stub += b"\x48\x8B\x43\x10"  # mov rax, [rbx+0x10]
    # mov [rip+disp32], rax  @ stub+7
    stub += b"\x48\x89\x05"
    disp_off = len(stub)
    stub += b"\x00\x00\x00\x00"
    # 清零重試計數（pool_slot+8）
    stub += b"\xC7\x05"
    retry_disp_off = len(stub)
    stub += b"\x00\x00\x00\x00\x00\x00\x00\x00"
    stub += b"\x4C\x8B\xF9"  # mov r15, rcx
    jmp_off = len(stub)
    rel = POOL_SAVE_CONTINUE_RVA - (cave_rva + jmp_off + 5)
    stub += b"\xE9" + struct.pack("<i", rel)
    # RIP 指向 disp 後一條指令
    rip_next = cave_rva + disp_off + 4
    disp = pool_slot_rva - rip_next
    struct.pack_into("<i", stub, disp_off, disp)
    rip_retry = cave_rva + retry_disp_off + 4
    struct.pack_into("<i", stub, retry_disp_off, (pool_slot_rva + 8) - rip_retry)
    return bytes(stub)


def _jmp_rel32(src_rva: int, dst_rva: int) -> bytes:
    return b"\xE9" + struct.pack("<i", dst_rva - (src_rva + 5))


def _rip_disp(rip_rva: int, target_rva: int) -> int:
    return target_rva - (rip_rva + 4)


def build_epic_check_stub(cave_rva: int, pool_slot_rva: int) -> bytes:
    stub = bytearray()

    def patch_rel32(off: int, target_rva: int) -> None:
        src = cave_rva + off + 4
        struct.pack_into("<i", stub, off, target_rva - src)

    def patch_rel8(off: int, target_rva: int) -> None:
        src = cave_rva + off + 1
        stub[off] = (target_rva - src) & 0xFF

    stub += b"\x48\x85\xFF"
    stub += b"\x0F\x84\x00\x00\x00\x00"
    je_null_disp = len(stub) - 4

    stub += b"\x48\x8B\x05\x00\x00\x00\x00"
    pool_disp = len(stub) - 4
    patch_rel32(pool_disp, pool_slot_rva)

    stub += b"\x48\x83\xF8\x04\x75\x00"
    jne_accept = len(stub) - 1
    stub += b"\x8B\x4F\x30"
    stub += b"\x83\xF9\x03\x74\x00"
    je_a = len(stub) - 1
    stub += b"\x83\xF9\x04\x74\x00"
    je_b = len(stub) - 1

    stub += b"\xFF\x05\x00\x00\x00\x00"
    retry_disp = len(stub) - 4
    patch_rel32(retry_disp, pool_slot_rva + 8)

    stub += b"\x81\x3D"
    cmp_disp = len(stub)
    stub += b"\x00\x00\x00\x00" + struct.pack("<I", MAX_RETRIES)
    patch_rel32(cmp_disp, pool_slot_rva + 8)

    stub += b"\x77\x00"
    ja_accept = len(stub) - 1
    stub += b"\xE9\x00\x00\x00\x00"
    jmp_retry_disp = len(stub) - 4

    accept = cave_rva + len(stub)
    stub += b"\xE9\x00\x00\x00\x00"
    jmp_cont_disp = len(stub) - 4

    patch_rel32(je_null_disp, POST_GET_ITEM_NULL_RVA)
    patch_rel8(jne_accept, accept)
    patch_rel8(je_a, accept)
    patch_rel8(je_b, accept)
    patch_rel8(ja_accept, accept)
    patch_rel32(jmp_retry_disp, RETRY_RVA)
    patch_rel32(jmp_cont_disp, POST_GET_ITEM_CONTINUE_RVA)
    return bytes(stub)


def _patch_unity_version_parser() -> None:
    """UnityPy 不認得本遊戲的 2022.3.62f2c1 字尾，讀取時裁掉 c1。"""
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


def _ensure_xijin_extra_epics(items: dict) -> int:
    existing_by_item_id = {int(item["itemID"]): item for item in items.values()}
    next_id = max(int(item["id"]) for item in items.values()) + 1
    added = 0

    for item_id in XIJIN_EXTRA_EPIC_ITEMS:
        item = existing_by_item_id.get(item_id)
        if item is None:
            item = {
                "id": next_id,
                "itemID": item_id,
                "itemCount": 1,
                "weight": 1000,
                "rare": EPIC_RARE_A,
                "guaranteeWeight": 1000,
                "smallGuaranteeWeight": 1000,
            }
            items[str(next_id)] = item
            next_id += 1
            added += 1
        else:
            item["itemCount"] = max(int(item.get("itemCount", 1)), 1)
            item["rare"] = EPIC_RARE_A
            item["weight"] = max(int(item.get("weight", 0)), 1000)
            item["guaranteeWeight"] = max(int(item.get("guaranteeWeight", 0)), 1000)
            item["smallGuaranteeWeight"] = max(int(item.get("smallGuaranteeWeight", 0)), 1000)

    return added


def _remove_xijin_epics(items: dict) -> int:
    removed_keys = [
        key
        for key, item in items.items()
        if int(item.get("itemID", 0)) in XIJIN_REMOVED_EPIC_ITEMS
    ]
    for key in removed_keys:
        del items[key]
    return len(removed_keys)


def _update_asset_map_size(bundle_size_without_prefix: int) -> None:
    if not ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP, ASSET_MAP_BACKUP)

    asset_map = json.loads(ASSET_MAP_BACKUP.read_text(encoding="utf-8"))
    if "size" in asset_map and "game_data.ab" in asset_map["size"]:
        asset_map["size"]["game_data.ab"] = bundle_size_without_prefix
    ASSET_MAP.write_text(json.dumps(asset_map, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def _patch_gacha_bundle() -> None:
    if not GAME_DATA_AB.exists():
        raise SystemExit(f"找不到 {GAME_DATA_AB}")
    if not GAME_DATA_BACKUP.exists():
        shutil.copy2(GAME_DATA_AB, GAME_DATA_BACKUP)
        print(f"  [backup] {GAME_DATA_BACKUP.name}")

    raw = GAME_DATA_BACKUP.read_bytes()
    if raw[:8] != b"OGODJ\x01\x00\x00":
        raise SystemExit("game_data.ab header 不符合預期，停止修補")

    _patch_unity_version_parser()
    env = UnityPy.load(raw[8:])

    _, pools = _load_text_asset_json(env, GACHA_POOL_ASSET)
    pool = pools.get(str(GACHA_POOL_XIJIN))
    if not pool:
        raise SystemExit(f"找不到 GachaPool id={GACHA_POOL_XIJIN}")

    gacha_name = pool["gachaName"]
    item_asset = f"{GACHA_ITEM_ASSET_PREFIX}{gacha_name}.json"
    item_obj, items = _load_text_asset_json(env, item_asset)

    removed_count = _remove_xijin_epics(items)
    epic_count = 0
    disabled_count = 0
    for item in items.values():
        if item.get("rare") in (EPIC_RARE_A, EPIC_RARE_B):
            # 使用固定正權重，避免原本史詩項目權重過小造成顯示或保底計算異常。
            item["weight"] = max(int(item.get("weight", 0)), 1000)
            item["guaranteeWeight"] = max(int(item.get("guaranteeWeight", 0)), 1000)
            item["smallGuaranteeWeight"] = max(int(item.get("smallGuaranteeWeight", 0)), 1000)
            epic_count += 1
        else:
            item["weight"] = 0
            item["guaranteeWeight"] = 0
            item["smallGuaranteeWeight"] = 0
            disabled_count += 1

    added_count = _ensure_xijin_extra_epics(items)

    _save_text_asset_json(item_obj, items)

    saved = next(iter(env.files.values())).save()
    GAME_DATA_AB.write_bytes(raw[:8] + saved)
    _update_asset_map_size(len(saved))

    extra_names = "、".join(XIJIN_EXTRA_EPIC_ITEMS.values())
    print(
        f"  [info] GachaPool {GACHA_POOL_XIJIN} -> {gacha_name}; "
        f"epic={epic_count}, disabled={disabled_count}, "
        f"extra_added={added_count}, removed={removed_count}"
    )
    print(f"  [info] 額外納入：{extra_names}")
    removed_names = "、".join(XIJIN_REMOVED_EPIC_ITEMS.values())
    print(f"  [info] 移出常駐希金池：{removed_names}")


def restore_gacha_data() -> None:
    restored = False
    if GAME_DATA_BACKUP.exists():
        shutil.copy2(GAME_DATA_BACKUP, GAME_DATA_AB)
        restored = True
    if ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP_BACKUP, ASSET_MAP)
        restored = True
    if restored:
        print("  [restore] GachaDataWeight game_data.ab")


def apply_gacha(data: bytearray, pe: pefile.PE) -> None:
    from game_data import GameDataSession
    from mods.gacha_defs import apply_gacha_xijin_pool

    session = GameDataSession()
    apply_gacha_xijin_pool(session)
    session.save()
    print("  [ok]   GachaDataWeight game_data.ab / GachaItemTabnew1")
