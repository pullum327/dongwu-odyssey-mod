#!/usr/bin/env python3
"""向後相容：請改用 apply_mods.py 或 mods_enabled.json。"""
from __future__ import annotations

from game_data import GameDataSession
from mod_registry import ALL_MODS, MOD_BY_ID


def apply_equipment_fixed_effects(data=None, pe=None) -> None:
    equipment_mod_ids = [m.id for m in ALL_MODS if m.category == "裝備"]
    session = GameDataSession()
    for mod_id in equipment_mod_ids:
        MOD_BY_ID[mod_id].apply(session)
    session.save()

    from mods.mod_texts import apply_shenwei_texts

    apply_shenwei_texts()
