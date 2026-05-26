"""火煉資料層備援：強制僅長明（flameId=2）可被抽選。"""
from __future__ import annotations

from game_data import GameDataSession

FLAME_ASSET = "assets/gamedata/equipmentenhanceflame.json"
CHANGMING_FLAME_ID = 2


def apply_ignite_changming_data(session: GameDataSession) -> None:
    flames = session.json(FLAME_ASSET)
    changed = 0
    for key, row in flames.items():
        fid = int(row.get("id", key))
        if fid == CHANGMING_FLAME_ID:
            if row.get("weight") != 10000:
                row["weight"] = 10000
                changed += 1
        elif row.get("weight", 0) != 0:
            row["weight"] = 0
            changed += 1
    print(f"  [ok]   ignite_changming_data 長明權重 10000（調整 {changed} 筆）")
