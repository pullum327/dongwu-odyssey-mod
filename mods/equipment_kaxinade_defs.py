"""Custom legendary weapon: Kaxinade's Sword (卡西納德之劍)."""
from __future__ import annotations

from pathlib import Path

from game_data import GameDataSession
from mods.polish_defs import SOUL_SIPHON_EFFECT_ID, apply_polish_soul_siphon
from mods.spriteatlas_patch import ICON_SPRITE_NAME, apply_sprite_replacement

EQUIPMENT_ASSET = "assets/gamedata/equipment.json"
ITEM_ASSET = "assets/gamedata/item.json"
EFFECT_ASSET = "assets/gamedata/equipmenteffect.json"
BUFF_ASSET = "assets/gamedata/buffs.json"
MODULE_ASSET = "assets/gamedata/module.json"
POOL_ASSET = "assets/gamedata/equipmenteffectpool.json"

MOD_ROOT = Path(__file__).resolve().parents[1]
KAXINADE_ICON_SOURCE = MOD_ROOT / "img" / "kaxinade_sword.png"

KAXINADE_EQUIPMENT_ID = 1510099
KAXINADE_ITEM_ID = 41510099
LEGENDARY_WEAPON_POLISH_POOL_ID = 51001

SPIRAL_STRIKE_EFFECT_ID = 7599004
# 開戰施加 buff（複製 10009）；裝備直掛 1104 無效，沿用 743802_GetBuff 傳 buffId
SPIRAL_STRIKE_BUFF_ID = 7599010
SPIRAL_GET_BUFF_MODULE_ID = 7599043
SPIRAL_GET_BUFF_FLOW = "743802_GetBuff"

CRIT_EFFECT_ID = 7100002
CRIT_EFFECT_REF = f"{CRIT_EFFECT_ID}_5"
SOUL_SIPHON_EFFECT_REF = f"{SOUL_SIPHON_EFFECT_ID}_1"
SPIRAL_EFFECT_REF = f"{SPIRAL_STRIKE_EFFECT_ID}_1"


def apply_equipment_kaxinade(session: GameDataSession) -> None:
    effects = session.json(EFFECT_ASSET)
    if str(SOUL_SIPHON_EFFECT_ID) not in effects:
        apply_polish_soul_siphon(session)
        effects = session.json(EFFECT_ASSET)

    _apply_spiral_strike_buff(session)
    _apply_spiral_strike_effect(session)
    _apply_kaxinade_polish_pool(session)
    _apply_kaxinade_equipment(session)
    _apply_kaxinade_item(session)
    _apply_kaxinade_icon()
    print(f"  [ok]   equipment_{KAXINADE_EQUIPMENT_ID} 卡西娜德之劍（傳奇武器）")


def _apply_spiral_strike_buff(session: GameDataSession) -> None:
    """複製 buff 10009（追加攻擊），由裝備詞條在回合開始施加。"""
    buffs = session.json(BUFF_ASSET)
    modules = session.json(MODULE_ASSET)
    ref = buffs.get("10009")
    if ref is None:
        raise SystemExit("找不到參考 buff 10009")
    buffs[str(SPIRAL_STRIKE_BUFF_ID)] = {
        **ref,
        "id": SPIRAL_STRIKE_BUFF_ID,
        "round": 99,
    }
    modules[str(SPIRAL_GET_BUFF_MODULE_ID)] = {
        "id": SPIRAL_GET_BUFF_MODULE_ID,
        "condition": 8,
        "components": 0,
        "param1": ["0"],
        "param2": ["0"],
        "restriction": [0],
        "restrictionValue": ["0"],
        "logic": 0,
        "flow": SPIRAL_GET_BUFF_FLOW,
        "count": 999,
        "name": "",
    }


def _apply_spiral_strike_effect(session: GameDataSession) -> None:
    effects = session.json(EFFECT_ASSET)

    effects[str(SPIRAL_STRIKE_EFFECT_ID)] = {
        "id": SPIRAL_STRIKE_EFFECT_ID,
        "name": "螺旋追斬",
        "describe": "單體攻擊技能額外造成一擊，傷害為原先的50%",
        "levelLimit": 1,
        "showInFilter": 1,
        "Lv1ModuleID": [SPIRAL_GET_BUFF_MODULE_ID],
        "Lv1Param1": [str(SPIRAL_STRIKE_BUFF_ID)],
        "Lv1Param2": [],
        "contentLv1": "單體攻擊技能額外造成一擊，傷害為原先的50%",
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


def _apply_kaxinade_polish_pool(session: GameDataSession) -> None:
    pools = session.json(POOL_ASSET)
    pools.pop(str(KAXINADE_EQUIPMENT_ID), None)

    pool = pools.get(str(LEGENDARY_WEAPON_POLISH_POOL_ID))
    if pool is None:
        raise SystemExit(f"找不到傳奇武器打磨池 {LEGENDARY_WEAPON_POLISH_POOL_ID}")

    effects = list(pool.get("effect", []))
    if SPIRAL_EFFECT_REF not in effects:
        effects.append(SPIRAL_EFFECT_REF)
        pool["effect"] = effects


def _apply_kaxinade_equipment(session: GameDataSession) -> None:
    equipment = session.json(EQUIPMENT_ASSET)
    equipment[str(KAXINADE_EQUIPMENT_ID)] = {
        "id": KAXINADE_EQUIPMENT_ID,
        "describe": "雙螺旋刃，單體斬擊再追一擊",
        "quality": 5,
        "equipmentPart": 1,
        "effectID": [
            SOUL_SIPHON_EFFECT_REF,
            CRIT_EFFECT_REF,
            SPIRAL_EFFECT_REF,
        ],
        "fixAttribute": ["101_4", "104_0.25"],
        "negativeAttribute": [],
        "polishTotal": 1,
        "polishInit": 1,
        "polishCountPoint": 0,
        "polishPoolID": LEGENDARY_WEAPON_POLISH_POOL_ID,
        "perfectAttribute": "101_4",
        "perfectAttributeProbability": 80000,
        "pricePolishUnfinished": ["100201_10", "100202_1"],
        "pricePolishFinished": ["100201_15", "100202_1"],
        "pricePolishPerfect": ["100201_20", "100202_3"],
        "scrappedPolishId": 4,
        "enhanceIgniteTag": ["weapon", "adventure"],
        "randomAttribute": 0,
        "randomAttributeCount": 0,
        "limitCharacterLevel": 0,
        "limitCharacter": [],
        "limitCharacterNation": [],
        "limitCharacterArea": [],
        "limitPowerLevel": 0,
    }


def _apply_kaxinade_item(session: GameDataSession) -> None:
    items = session.json(ITEM_ASSET)
    items[str(KAXINADE_ITEM_ID)] = {
        "id": KAXINADE_ITEM_ID,
        "name": "卡西娜德之劍",
        "desc": "雙螺旋刃，單體斬擊再追一擊",
        "value": 0,
        "rewardPool": [],
        "weight": 0,
        "priceVal": 2,
        "equipmentID": KAXINADE_EQUIPMENT_ID,
        "stack": 1,
        "questLimit": 0,
        "questUseLimit": 1,
        "itemType": 6,
        "icon": ICON_SPRITE_NAME,
        "itemImage": ICON_SPRITE_NAME,
        "quality": 5,
        "priceCoinID": 100201,
        "showFastTips": 1,
        "useType": 0,
        "useResult": 0,
        "useCount": 1,
        "useCD": 0,
        "areaLimitType": 0,
        "areaLimitID": [],
        "keyCharacters": [],
        "keyItemID": [],
        "keyItemRequireCount": [],
        "keyItemConsumeCount": [],
        "expireType": 0,
        "expireVal": 0,
        "expireFixedTime": "",
        "expireItemID": -1,
        "storable": 1,
        "discard": 1,
        "tag": [],
    }


def _apply_kaxinade_icon() -> None:
    if not KAXINADE_ICON_SOURCE.exists():
        raise SystemExit(f"找不到圖示原始檔：{KAXINADE_ICON_SOURCE}")
    apply_sprite_replacement(ICON_SPRITE_NAME, KAXINADE_ICON_SOURCE)
