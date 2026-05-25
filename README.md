# 東吳大冒險 — 本機 Mod 修補

修改 `GameAssembly.dll`（IL2CPP）與 `game_data.ab`（資料）。**請先關閉遊戲**再套用；Steam 更新後需重新執行。

## 模組化套用（推薦）

各功能已拆成獨立 mod，透過 [`mods_enabled.json`](mods_enabled.json) 開關：

```powershell
python "_ignite_mod\apply_mods.py" --list
python "_ignite_mod\apply_mods.py"
python "_ignite_mod\apply_mods.py" --only ignite_no_consume,enemy_hp_multiplier   # 單次套用，不改設定
python "_ignite_mod\apply_mods.py" --disable gacha_xijin_pool --save             # 寫入 mods_enabled.json
python "_ignite_mod\apply_mods.py" --restore
```

或直接編輯 `mods_enabled.json`，將不需要的 mod 設為 `false` 後執行 `apply_mods.py`。

**如何自行修改卡池、火煉、裝備數值？** 見 [`CUSTOMIZATION.md`](CUSTOMIZATION.md)。

[`apply_all_mods.py`](apply_all_mods.py) 與 [`套用全部Mod.bat`](套用全部Mod.bat) 仍可用，等同套用 `mods_enabled.json` 中所有 **ON** 的 mod。

---

## Mod 一覽

| 分類 | Mod ID | 說明 |
|------|--------|------|
| 火煉 | `ignite_no_consume` | 不消耗材料、可空材料、UI 檢查通過 |
| 火煉 | `ignite_changming_triple` | 4 條長明、正面數值 ×3 |
| 打磨 | `polish_max_level` | 打磨詞條固定為 levelLimit 滿級 |
| 打磨 | `polish_soul_siphon` | 自定義詞條「靈魂虹吸」加入全部打磨池 |
| 怪物 | `enemy_hp_multiplier` | 強力怪物 (size=2) / 首領 (character=99) 血量 ×2 |
| 卡池 | `gacha_xijin_pool` | 希金交易會池 4 權重修補 |
| 造型 | `costume_default_models` | 部分角色預設課金造型 |
| 裝備 | `equipment_1410009` | 八十弦月夜花霧 |
| 裝備 | `equipment_1530001` | 維利亞舞鞋 |
| 裝備 | `equipment_1420017` | 索羅輕甲 |
| 裝備 | `equipment_1510003` | 西北望（含神威） |
| 裝備 | `equipment_1430003` | 大世界法典 |
| 裝備 | `equipment_1430013` | 巨蜥骨飾 |
| 裝備 | `equipment_1430021` | 蠻野口籠 |
| 裝備 | `equipment_1520002` | 柔光紗衣 |
| 裝備 | `equipment_1430008` | 名伶殘羽 |
| 裝備 | `equipment_effect_7400023` | 自愈詞條 3 級強化 |

---

## 目錄結構

```
_ignite_mod/
  apply_mods.py          # 主入口（選擇性套用）
  apply_all_mods.py      # 套用全部已啟用 mod
  mods_enabled.json      # 開關設定
  mod_registry.py        # mod 註冊表
  game_data.py           # game_data.ab 共用工作階段
  mods/
    equipment_defs.py    # 各裝備 mod 實作
    polish_defs.py       # 打磨 mod
    enemy_defs.py        # 怪物血量
    gacha_defs.py        # 卡池
    costume_defs.py      # 造型
    mod_texts.py         # 自定義詞條 UI 文案
  patch_ignite.py        # 火煉 DLL patch（可拆成兩 mod）
  patch_common.py        # DLL 共用工具
```

---

## 還原

```powershell
python "_ignite_mod\apply_mods.py" --restore
```

或手動覆蓋 `GameAssembly.dll.ignite_mod.bak` → `GameAssembly.dll`。

---

## 僅火煉

```powershell
python "_ignite_mod\apply_ignite_only.py"
```

等同 `--only ignite_no_consume,ignite_changming_triple`。

---

## 依賴

```powershell
pip install pefile keystone-engine UnityPy
```

## 風險

修改遊戲二進位可能違反使用者條款；請自行承擔風險並僅用於單機／離線測試。
