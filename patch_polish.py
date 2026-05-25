#!/usr/bin/env python3
"""向後相容：請改用 apply_mods.py。"""
from __future__ import annotations

from game_data import GameDataSession
from mods.polish_defs import apply_polish_max_level, apply_polish_soul_siphon
from mods.mod_texts import apply_soul_siphon_texts


def apply_polish(data=None, pe=None) -> None:
    session = GameDataSession()
    apply_polish_max_level(session)
    apply_polish_soul_siphon(session)
    session.save()
    apply_soul_siphon_texts()
