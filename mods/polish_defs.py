"""Custom polish mods."""
from __future__ import annotations

from game_data import GameDataSession

EFFECT_ASSET = "assets/gamedata/equipmenteffect.json"
MODULE_ASSET = "assets/gamedata/module.json"
POOL_ASSET = "assets/gamedata/equipmenteffectpool.json"

SOUL_SIPHON_EFFECT_ID = 7599003
SOUL_SIPHON_EFFECT_REF = f"{SOUL_SIPHON_EFFECT_ID}_1"
SOUL_SIPHON_MODULES = (7599031, 7599032)


def apply_polish_max_level(session: GameDataSession) -> None:
    effects = session.json(EFFECT_ASSET)
    pools = session.json(POOL_ASSET)

    level_limits = {
        int(effect["id"]): int(effect.get("levelLimit", 1))
        for effect in effects.values()
        if int(effect.get("levelLimit", 1)) > 0
    }

    changed = 0
    total = 0
    for pool in pools.values():
        rewritten: list[str] = []
        for item in pool.get("effect", []):
            updated, did_change = _rewrite_effect_level(item, level_limits)
            rewritten.append(updated)
            changed += int(did_change)
            total += 1
        pool["effect"] = rewritten

        perfect = pool.get("perfectEffect", "")
        if perfect:
            updated, did_change = _rewrite_effect_level(perfect, level_limits)
            pool["perfectEffect"] = updated
            changed += int(did_change)
            total += 1

    print(f"  [ok]   polish_max_level {changed}/{total} 個詞條改為 levelLimit")


def apply_polish_soul_siphon(session: GameDataSession) -> None:
    effects = session.json(EFFECT_ASSET)
    modules = session.json(MODULE_ASSET)
    pools = session.json(POOL_ASSET)

    modules[str(SOUL_SIPHON_MODULES[0])] = {
        "id": SOUL_SIPHON_MODULES[0],
        "condition": 0,
        "components": 1022,
        "param1": ["0"],
        "param2": ["0"],
        "restriction": [0],
        "restrictionValue": ["0"],
        "logic": 0,
        "flow": "",
        "count": 999,
        "name": "",
    }
    modules[str(SOUL_SIPHON_MODULES[1])] = {
        "id": SOUL_SIPHON_MODULES[1],
        "condition": 0,
        "components": 1113,
        "param1": ["0"],
        "param2": ["0"],
        "restriction": [0],
        "restrictionValue": ["0"],
        "logic": 0,
        "flow": "",
        "count": 999,
        "name": "",
    }

    effects[str(SOUL_SIPHON_EFFECT_ID)] = {
        "id": SOUL_SIPHON_EFFECT_ID,
        "name": "靈魂虹吸",
        "describe": "造成傷害時回復傷害的血量，並提高最終傷害",
        "levelLimit": 1,
        "showInFilter": 1,
        "Lv1ModuleID": list(SOUL_SIPHON_MODULES),
        "Lv1Param1": ["0.12", "0.3"],
        "Lv1Param2": [],
        "contentLv1": "造成傷害時回復傷害的<param1[0].p>血量；最終傷害+<param1[1].p>",
        "Lv2ModuleID": [],
        "Lv2Param1": [],
        "Lv2Param2": [],
        "contentLv2": "",
        "Lv3ModuleID": [],
        "Lv3Param1": [],
        "Lv3Param2": [],
        "contentLv3": "",
        "Lv4ModuleID": [],
        "Lv4Param1": [],
        "Lv4Param2": [],
        "contentLv4": "",
        "Lv5ModuleID": [],
        "Lv5Param1": [],
        "Lv5Param2": [],
        "contentLv5": "",
        "Lv6ModuleID": [],
        "Lv6Param1": [],
        "Lv6Param2": [],
        "contentLv6": "",
        "priority": 0,
    }

    pools_added = 0
    for pool in pools.values():
        effects_list = pool.get("effect", [])
        if SOUL_SIPHON_EFFECT_REF not in effects_list:
            effects_list.append(SOUL_SIPHON_EFFECT_REF)
            pool["effect"] = effects_list
            pools_added += 1

    print(f"  [ok]   polish_soul_siphon 靈魂虹吸加入 {pools_added} 個打磨池")


def _rewrite_effect_level(raw: str, level_limits: dict[int, int]) -> tuple[str, bool]:
    try:
        effect_id_text, _level_text = raw.split("_", 1)
        effect_id = int(effect_id_text)
    except ValueError:
        return raw, False

    max_level = level_limits.get(effect_id)
    if not max_level:
        return raw, False

    updated = f"{effect_id}_{max_level}"
    return updated, updated != raw
