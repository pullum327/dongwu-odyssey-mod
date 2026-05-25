"""Individual equipment stat/effect mods (one mod per equipment)."""
from __future__ import annotations

from game_data import GameDataSession

EQUIPMENT_ASSET = "assets/gamedata/equipment.json"
EFFECT_ASSET = "assets/gamedata/equipmenteffect.json"
MODULE_ASSET = "assets/gamedata/module.json"

YASO_MOONFLOWER_ID = 1410009


def apply_equipment_yaso_moonflower(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(YASO_MOONFLOWER_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={YASO_MOONFLOWER_ID}")
    item["effectID"] = ["7400021_3"]
    item["fixAttribute"] = ["101_7", "104_0.3", "102_0.3"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{YASO_MOONFLOWER_ID} 八十弦月夜花霧")


VILIA_DANCE_SHOES_ID = 1530001


def apply_equipment_vilia_dance_shoes(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(VILIA_DANCE_SHOES_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={VILIA_DANCE_SHOES_ID}")
    item["effectID"] = ["7500001_1", "7100002_5", "7400012_3"]
    item["fixAttribute"] = ["301_6", "104_0.15", "105_0.5", "213_0.5"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{VILIA_DANCE_SHOES_ID} 維利亞舞鞋")


SOLUO_LIGHT_ARMOR_ID = 1420017


def apply_equipment_soluo_light_armor(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(SOLUO_LIGHT_ARMOR_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={SOLUO_LIGHT_ARMOR_ID}")
    item["fixAttribute"] = ["201_15", "202_0.15", "213_0.5", "301_6"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{SOLUO_LIGHT_ARMOR_ID} 索羅輕甲")


XIBEIWANG_ID = 1510003
SHENWEI_EFFECT_ID = 7599002
SHENWEI_MODULES = (7599021, 7599022, 7599023)


def apply_equipment_xibeiwang(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    effects = session.json(EFFECT_ASSET)
    modules = session.json(MODULE_ASSET)

    for module_id, component in zip(SHENWEI_MODULES, (1126, 1127, 1008), strict=True):
        modules[str(module_id)] = {
            "id": module_id,
            "condition": 0,
            "components": component,
            "param1": ["0"],
            "param2": ["0"],
            "restriction": [0],
            "restrictionValue": ["0"],
            "logic": 0,
            "flow": "",
            "count": 999,
            "name": "",
        }

    effects[str(SHENWEI_EFFECT_ID)] = {
        "id": SHENWEI_EFFECT_ID,
        "name": "神威",
        "describe": "提高反擊&追擊傷害和速度",
        "levelLimit": 1,
        "showInFilter": 1,
        "Lv1ModuleID": list(SHENWEI_MODULES),
        "Lv1Param1": ["0.5", "0.5", "3"],
        "Lv1Param2": [],
        "contentLv1": "反擊&追擊傷害+<param1[0].p>，速度+<param1[2]>",
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

    item = equipment.get(str(XIBEIWANG_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={XIBEIWANG_ID}")
    item["effectID"] = ["7500004_1", "7400003_3", f"{SHENWEI_EFFECT_ID}_1"]
    item["fixAttribute"] = ["101_8", "102_0.2", "301_3"]
    item["negativeAttribute"] = ["104_-0.3"]
    print(f"  [ok]   equipment_{XIBEIWANG_ID} 西北望 + 神威")


WORLD_CODEX_ID = 1430003


def apply_equipment_world_codex(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(WORLD_CODEX_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={WORLD_CODEX_ID}")
    item["fixAttribute"] = ["101_1", "103_0.15", "105_0.15", "102_0.15"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{WORLD_CODEX_ID} 大世界法典")


GIANT_LIZARD_BONE_ID = 1430013


def apply_equipment_giant_lizard_bone(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(GIANT_LIZARD_BONE_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={GIANT_LIZARD_BONE_ID}")
    item["fixAttribute"] = ["101_1", "103_0.5"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{GIANT_LIZARD_BONE_ID} 巨蜥骨飾")


SAVAGE_MUZZLE_ID = 1430021


def apply_equipment_savage_muzzle(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(SAVAGE_MUZZLE_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={SAVAGE_MUZZLE_ID}")
    item["fixAttribute"] = ["101_1", "406_0.5"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{SAVAGE_MUZZLE_ID} 蠻野口籠")


SOFT_LIGHT_ROBE_ID = 1520002


def apply_equipment_soft_light_robe(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(SOFT_LIGHT_ROBE_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={SOFT_LIGHT_ROBE_ID}")
    item["effectID"] = ["7500009_1", "7400013_3", "7100005_5"]
    item["fixAttribute"] = ["201_15", "104_0.15", "111_0.5"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{SOFT_LIGHT_ROBE_ID} 柔光紗衣")


ACTOR_FEATHER_ID = 1430008


def apply_equipment_actor_feather(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    item = equipment.get(str(ACTOR_FEATHER_ID))
    if item is None:
        raise SystemExit(f"找不到 Equipment id={ACTOR_FEATHER_ID}")
    item["fixAttribute"] = ["301_3", "111_0.5", "106_0.5"]
    item["negativeAttribute"] = []
    print(f"  [ok]   equipment_{ACTOR_FEATHER_ID} 名伶殘羽")
