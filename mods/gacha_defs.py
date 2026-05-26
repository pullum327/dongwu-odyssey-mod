"""Gacha pool mod."""
from __future__ import annotations

from game_data import GameDataSession

GACHA_POOL_XIJIN = 4
EPIC_RARE_A = 3
EPIC_RARE_B = 4

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
    41510099: "卡西娜德之劍",
}

GACHA_POOL_ASSET = "assets/gamedata/gachapool.json"
GACHA_ITEM_ASSET_PREFIX = "assets/gamedata/gachaitemtab"


def apply_gacha_xijin_pool(session: GameDataSession) -> None:
    pools = session.json(GACHA_POOL_ASSET)
    pool = pools.get(str(GACHA_POOL_XIJIN))
    if not pool:
        raise SystemExit(f"找不到 GachaPool id={GACHA_POOL_XIJIN}")

    gacha_name = pool["gachaName"]
    item_asset = f"{GACHA_ITEM_ASSET_PREFIX}{gacha_name}.json"
    items = session.json(item_asset)

    removed_count = _remove_xijin_epics(items)
    epic_count = 0
    disabled_count = 0
    for item in items.values():
        if item.get("rare") in (EPIC_RARE_A, EPIC_RARE_B):
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

    extra_names = "、".join(XIJIN_EXTRA_EPIC_ITEMS.values())
    removed_names = "、".join(XIJIN_REMOVED_EPIC_ITEMS.values())
    print(
        f"  [ok]   gacha_xijin_pool epic={epic_count}, disabled={disabled_count}, "
        f"extra={added_count}, removed={removed_count}"
    )
    print(f"  [info] 額外納入：{extra_names}")
    print(f"  [info] 移出：{removed_names}")


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
