# 東吳大冒險 — 本機 Mod 修補

修改 `GameAssembly.dll`（IL2CPP）與 `game_data.ab`（資料）。**請先關閉遊戲**再套用；Steam 更新後需重新執行。

## 模組化套用

各功能已拆成獨立 mod，透過 [`mods_enabled.json`](mods_enabled.json) 開關：

```powershell
python "_ignite_mod\apply_mods.py" --list
python "_ignite_mod\apply_mods.py"
python "_ignite_mod\apply_mods.py" --only ignite_no_consume,enemy_hp_multiplier
python "_ignite_mod\apply_mods.py" --disable gacha_xijin_pool --save
python "_ignite_mod\apply_mods.py" --restore
```

**如何自行修改卡池、火煉、裝備？** 見 [`CUSTOMIZATION.md`](CUSTOMIZATION.md)。

雙擊 [`套用全部Mod.bat`](套用全部Mod.bat) 等同執行 `apply_mods.py`。

---

## Mod 一覽

| 分類 | Mod ID | 說明 |
|------|--------|------|
| 火煉 | `ignite_no_consume` | 不消耗材料、可空材料 |
| 火煉 | `ignite_changming_triple` | 4 條長明、正面數值 ×3 |
| 打磨 | `polish_max_level` | 打磨詞條固定滿級 |
| 打磨 | `polish_soul_siphon` | 靈魂虹吸（全部打磨池） |
| 怪物 | `enemy_hp_multiplier` | 強力/Boss 血量 ×2 |
| 卡池 | `gacha_xijin_pool` | 希金交易會池 4 |
| 造型 | `costume_default_models` | 預設課金造型 |
| 裝備 | `equipment_*` | 各裝備獨立 mod（見 registry） |

---

## 目錄結構

```
_ignite_mod/
  apply_mods.py          # 唯一入口
  mods_enabled.json      # 開關設定
  mod_registry.py        # mod 註冊表
  game_data.py           # game_data.ab 工作階段
  patch_ignite.py        # 火煉 DLL patch
  patch_common.py        # DLL 工具
  mods/                  # 各 mod 實作
  CUSTOMIZATION.md       # 自訂修改指南
```

---

## 依賴

```powershell
pip install pefile keystone-engine UnityPy
```

## 風險

修改遊戲二進位可能違反使用者條款；請自行承擔風險並僅用於單機／離線測試。
