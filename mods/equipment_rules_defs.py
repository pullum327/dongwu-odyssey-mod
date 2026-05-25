"""Quality 5 (legendary) equipment rule overrides."""
from __future__ import annotations

from game_data import GameDataSession

GLOBAL_CONFIG_ASSET = "assets/gamedata/globalconfig.json"
EQUIPMENT_ASSET = "assets/gamedata/equipment.json"

LEGENDARY_QUALITY = 5
LEGENDARY_SUM_LIMIT_KEY = "EquipmentLegendarySumLimit"

PART_IGNITE_TAGS: dict[int, list[str]] = {
    1: ["weapon", "adventure"],
    2: ["armour", "adventure"],
    3: ["jewelry", "adventure"],
}


def apply_equipment_quality5_rules(session: GameDataSession) -> None:
    global_config = session.json(GLOBAL_CONFIG_ASSET)
    limit_entry = global_config.get(LEGENDARY_SUM_LIMIT_KEY)
    if limit_entry is None:
        raise SystemExit(f"找不到 globalconfig 項目 {LEGENDARY_SUM_LIMIT_KEY}")

    old_limit = str(limit_entry.get("value", ""))
    if old_limit != "0":
        limit_entry["value"] = "0"
        print(f"  [ok]   equipment_quality5_rules {LEGENDARY_SUM_LIMIT_KEY} {old_limit} -> 0（不限制件數）")
    else:
        print(f"  [ok]   equipment_quality5_rules {LEGENDARY_SUM_LIMIT_KEY} 已是 0")

    equipment = session.json(EQUIPMENT_ASSET)
    ignite_changed = 0
    ignite_skipped = 0
    for item in equipment.values():
        if item.get("quality") != LEGENDARY_QUALITY:
            continue
        part = int(item.get("equipmentPart", 0))
        tags = PART_IGNITE_TAGS.get(part)
        if tags is None:
            ignite_skipped += 1
            continue
        if item.get("enhanceIgniteTag") != tags:
            item["enhanceIgniteTag"] = tags
            ignite_changed += 1

    print(
        "  [ok]   equipment_quality5_rules "
        f"quality=5 火煉標籤 {ignite_changed} 件"
        + (f"（略過未知部位 {ignite_skipped} 件）" if ignite_skipped else "")
    )
