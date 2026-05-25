#!/usr/bin/env python3
"""向後相容：請改用 apply_mods.py。"""
from __future__ import annotations

from game_data import GameDataSession
from mods.enemy_defs import apply_enemy_hp_multiplier


def apply_strong_enemy_hp(data=None, pe=None) -> None:
    session = GameDataSession()
    apply_enemy_hp_multiplier(session)
    session.save()
