"""Enemy HP multiplier mod."""
from __future__ import annotations

from game_data import GameDataSession

ENEMY_ASSET = "assets/gamedata/enemy.json"

STRONG_ENEMY_SIZE = 2
BOSS_CHARACTER_TYPE = 99
ENEMY_HP_MULTIPLIER = 2
CORPSE_CHARACTER_TYPE = 2
SKIP_NAME_PARTS = ("木桩", "木樁", "尸体", "屍体", "屍體")


def _should_skip_enemy(enemy: dict) -> bool:
    if enemy.get("character") == CORPSE_CHARACTER_TYPE:
        return True
    name = str(enemy.get("name", ""))
    return any(part in name for part in SKIP_NAME_PARTS)


def _needs_hp_multiplier(enemy: dict) -> bool:
    if _should_skip_enemy(enemy):
        return False
    return enemy.get("size") == STRONG_ENEMY_SIZE or enemy.get("character") == BOSS_CHARACTER_TYPE


def apply_enemy_hp_multiplier(session: GameDataSession) -> None:
    enemies = session.json(ENEMY_ASSET)

    changed_strong = 0
    changed_boss = 0
    for enemy in enemies.values():
        if not _needs_hp_multiplier(enemy):
            continue
        hp = enemy.get("hp")
        if not isinstance(hp, (int, float)) or hp <= 0:
            continue
        new_hp = int(hp * ENEMY_HP_MULTIPLIER)
        if new_hp == hp:
            continue
        enemy["hp"] = new_hp
        if enemy.get("character") == BOSS_CHARACTER_TYPE:
            changed_boss += 1
        if enemy.get("size") == STRONG_ENEMY_SIZE:
            changed_strong += 1

    print(
        "  [ok]   enemy_hp_multiplier "
        f"強力 {changed_strong} 個、首領 {changed_boss} 個，x{ENEMY_HP_MULTIPLIER}"
    )
