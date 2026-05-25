"""Global equipment effect mods (not tied to a single piece of gear)."""
from __future__ import annotations

from game_data import GameDataSession

EFFECT_ASSET = "assets/gamedata/equipmenteffect.json"
MODULE_ASSET = "assets/gamedata/module.json"

SELF_HEAL_EFFECT_ID = 7400023
SELF_HEAL_MIASMA_MODULE_ID = 742303


def apply_effect_self_heal(session: GameDataSession) -> None:
    effects = session.json(EFFECT_ASSET)
    modules = session.json(MODULE_ASSET)

    modules[str(SELF_HEAL_MIASMA_MODULE_ID)] = {
        "id": SELF_HEAL_MIASMA_MODULE_ID,
        "condition": 15,
        "components": 1003,
        "param1": ["0"],
        "param2": ["0"],
        "restriction": [0],
        "restrictionValue": ["0"],
        "logic": 0,
        "flow": "",
        "count": 999,
        "name": "",
    }

    self_heal = effects.get(str(SELF_HEAL_EFFECT_ID))
    if self_heal is None:
        raise SystemExit(f"找不到 EquipmentEffect id={SELF_HEAL_EFFECT_ID}")

    self_heal["Lv3ModuleID"] = [742301, SELF_HEAL_MIASMA_MODULE_ID]
    self_heal["Lv3Param1"] = ["12", "-10"]
    self_heal["Lv3Param2"] = []
    self_heal["contentLv3"] = "恢復<param1[0]>點生命值；恢復10點瘴氣"
    print(f"  [ok]   effect_self_heal 自愈 {SELF_HEAL_EFFECT_ID} 3級強化")
