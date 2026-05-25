"""Mod registry — each entry is an independently toggleable mod."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

import pefile

from game_data import GameDataSession
from mods.costume_defs import apply_costume_default_models
from mods.enemy_defs import apply_enemy_hp_multiplier
from mods.equipment_defs import (
    apply_equipment_actor_feather,
    apply_equipment_effect_self_heal,
    apply_equipment_giant_lizard_bone,
    apply_equipment_savage_muzzle,
    apply_equipment_soft_light_robe,
    apply_equipment_soluo_light_armor,
    apply_equipment_vilia_dance_shoes,
    apply_equipment_world_codex,
    apply_equipment_xibeiwang,
    apply_equipment_yaso_moonflower,
)
from mods.gacha_defs import apply_gacha_xijin_pool
from mods.mod_texts import apply_costume_texts, apply_shenwei_texts, apply_soul_siphon_texts
from mods.polish_defs import apply_polish_max_level, apply_polish_soul_siphon
from patch_ignite import apply_ignite_changming_triple, apply_ignite_no_consume

ModKind = Literal["dll", "game_data", "strings"]


@dataclass(frozen=True)
class ModSpec:
    id: str
    name: str
    category: str
    kind: ModKind
    apply: Callable[..., None]


def _apply_ignite_no_consume(pe: pefile.PE, data: bytearray, backup: bytes) -> None:
    apply_ignite_no_consume(pe, data, backup)


def _apply_ignite_changming(pe: pefile.PE, data: bytearray, backup: bytes) -> None:
    apply_ignite_changming_triple(pe, data, backup)


ALL_MODS: tuple[ModSpec, ...] = (
    ModSpec(
        "ignite_no_consume",
        "火煉不消耗材料",
        "火煉",
        "dll",
        _apply_ignite_no_consume,
    ),
    ModSpec(
        "ignite_changming_triple",
        "火煉長明 ×3 數值",
        "火煉",
        "dll",
        _apply_ignite_changming,
    ),
    ModSpec(
        "polish_max_level",
        "打磨詞條固定滿級",
        "打磨",
        "game_data",
        apply_polish_max_level,
    ),
    ModSpec(
        "polish_soul_siphon",
        "自定義打磨：靈魂虹吸",
        "打磨",
        "game_data",
        apply_polish_soul_siphon,
    ),
    ModSpec(
        "enemy_hp_multiplier",
        "強力怪物 / 首領血量 ×2",
        "怪物",
        "game_data",
        apply_enemy_hp_multiplier,
    ),
    ModSpec(
        "gacha_xijin_pool",
        "希金交易會卡池",
        "卡池",
        "game_data",
        apply_gacha_xijin_pool,
    ),
    ModSpec(
        "costume_default_models",
        "角色預設課金造型",
        "造型",
        "game_data",
        apply_costume_default_models,
    ),
    ModSpec(
        "equipment_1410009",
        "八十弦月夜花霧",
        "裝備",
        "game_data",
        apply_equipment_yaso_moonflower,
    ),
    ModSpec(
        "equipment_1530001",
        "維利亞舞鞋",
        "裝備",
        "game_data",
        apply_equipment_vilia_dance_shoes,
    ),
    ModSpec(
        "equipment_1420017",
        "索羅輕甲",
        "裝備",
        "game_data",
        apply_equipment_soluo_light_armor,
    ),
    ModSpec(
        "equipment_1510003",
        "西北望（含神威）",
        "裝備",
        "game_data",
        apply_equipment_xibeiwang,
    ),
    ModSpec(
        "equipment_1430003",
        "大世界法典",
        "裝備",
        "game_data",
        apply_equipment_world_codex,
    ),
    ModSpec(
        "equipment_1430013",
        "巨蜥骨飾",
        "裝備",
        "game_data",
        apply_equipment_giant_lizard_bone,
    ),
    ModSpec(
        "equipment_1430021",
        "蠻野口籠",
        "裝備",
        "game_data",
        apply_equipment_savage_muzzle,
    ),
    ModSpec(
        "equipment_1520002",
        "柔光紗衣",
        "裝備",
        "game_data",
        apply_equipment_soft_light_robe,
    ),
    ModSpec(
        "equipment_1430008",
        "名伶殘羽",
        "裝備",
        "game_data",
        apply_equipment_actor_feather,
    ),
    ModSpec(
        "equipment_effect_7400023",
        "自愈詞條 3 級強化",
        "裝備",
        "game_data",
        apply_equipment_effect_self_heal,
    ),
)

MOD_BY_ID = {mod.id: mod for mod in ALL_MODS}

# 文案 mod（跟著對應 game_data mod 自動套用）
STRING_MODS: dict[str, Callable[[], None]] = {
    "equipment_1510003": apply_shenwei_texts,
    "polish_soul_siphon": apply_soul_siphon_texts,
    "costume_default_models": apply_costume_texts,
}

DEFAULT_ENABLED = {mod.id: True for mod in ALL_MODS}
