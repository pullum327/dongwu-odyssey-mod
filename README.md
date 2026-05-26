# 東吳大冒險 Mod（`_ignite_mod` + BepInEx）

**GitHub：** https://github.com/pullum327/dongwu-odyssey-mod  
**BepInEx 發佈包：** https://github.com/pullum327/dongwu-odyssey-mod/releases/tag/bepinex-mod-rv0

玩家安裝請用 Release 內的 zip，**不需 Python**。本資料夾供開發者改數值、合併 `game_data.ab` 與建包。

---

## BepInEx 插件目錄結構

每個 mod 對應一個資料夾：

```
BepInEx/plugins/<mod_id>/
  DongwuOdyssey.Mod.<mod_id>.dll    ← 主插件（必備）
  dongwu-data-mod.txt               ← 資料 mod 才有；內容為 mod id 或 *
```

**共用 DLL（依類型複製到插件資料夾）：**

| DLL | 哪些 mod 需要 |
|-----|----------------|
| `DongwuOdyssey.ModCore.dll` | 所有資料 mod + `dongwu_data_core` |
| `DongwuOdyssey.HarmonyLib.dll` | 僅 `ignite_no_consume`、`ignite_changming_triple` |

資料 mod 的實際改動已寫入 `game_data.ab` 等檔案（建包時合併）；BepInEx 插件主要用來**宣告**已安裝哪些 mod，並在 log 中記錄。

---

## Mod 一覽

### 核心與 Harmony（執行期靠 DLL）

| mod id | 插件資料夾 | 主 DLL | 額外 DLL | 功能 |
|--------|------------|--------|----------|------|
| `dongwu_data_core` | `dongwu_data_core/` | `DongwuOdyssey.Mod.dongwu_data_core.dll` | `DongwuOdyssey.ModCore.dll` | 資料 mod 核心：啟動時掃描已安裝的 `dongwu-data-mod.txt` 並寫入 log（玩家端不跑 Python） |
| `ignite_no_consume` | `ignite_no_consume/` | `DongwuOdyssey.Mod.ignite_no_consume.dll` | `ModCore.dll`、`HarmonyLib.dll` | 火煉不消耗材料 |
| `ignite_changming_triple` | `ignite_changming_triple/` | `DongwuOdyssey.Mod.ignite_changming_triple.dll` | `ModCore.dll`、`HarmonyLib.dll` | 火煉必出長明，且長明詞條數值 ×3 |

Harmony 實作：`DongwuOdyssey.BepInEx/HarmonyLib/IgniteNoConsumePatches.cs`、`IgniteChangmingPatches.cs`。

### 資料 mod（建包寫入 game_data；插件 + 已合併資料檔）

| mod id | 主 DLL | 功能 | Python 實作 |
|--------|--------|------|-------------|
| `data_combined` | `DongwuOdyssey.Mod.data_combined.dll` | 宣告檔為 `*`，代表啟用下方全部資料 mod（與逐個安裝等效） | — |
| `ignite_changming_data` | `DongwuOdyssey.Mod.ignite_changming_data.dll` | 火煉資料層：僅長明（flameId=2）有權重，其餘火焰權重歸零 | `mods/ignite_data_defs.py` |
| `polish_max_level` | `DongwuOdyssey.Mod.polish_max_level.dll` | 打磨池詞條一律抽滿該 effect 的 `levelLimit` | `mods/polish_defs.py` |
| `polish_soul_siphon` | `DongwuOdyssey.Mod.polish_soul_siphon.dll` | 新增「靈魂虹吸」詞條並加入各打磨池（含文案） | `mods/polish_defs.py`、`mods/mod_texts.py` |
| `effect_self_heal` | `DongwuOdyssey.Mod.effect_self_heal.dll` | 強化「自愈」詞條（3 級效果） | `mods/effect_defs.py` |
| `equipment_quality5_rules` | `DongwuOdyssey.Mod.equipment_quality5_rules.dll` | 傳奇裝備多件穿戴、傳奇部位可火煉 | `mods/equipment_rules_defs.py` |
| `enemy_hp_multiplier` | `DongwuOdyssey.Mod.enemy_hp_multiplier.dll` | 強力怪／首領 HP ×2（略過木桩、屍體等） | `mods/enemy_defs.py` |
| `gacha_xijin_pool` | `DongwuOdyssey.Mod.gacha_xijin_pool.dll` | 希金交易會卡池：僅保留指定史詩裝備，移出其他史詩 | `mods/gacha_defs.py` |
| `costume_default_models` | `DongwuOdyssey.Mod.costume_default_models.dll` | 部分角色預設為課金造型模型（含語系文案） | `mods/costume_defs.py`、`mods/mod_texts.py` |

### 單件裝備 mod（`game_data` 改屬性／效果）

| mod id | 裝備 | 主 DLL | 功能 | Python 實作 |
|--------|------|--------|------|-------------|
| `equipment_1410009` | 八十弦月夜花霧 (1410009) | `DongwuOdyssey.Mod.equipment_1410009.dll` | 自訂 effect／屬性 | `mods/equipment_defs.py` |
| `equipment_1530001` | 維利亞舞鞋 (1530001) | `DongwuOdyssey.Mod.equipment_1530001.dll` | 自訂 effect／屬性 | `mods/equipment_defs.py` |
| `equipment_1420017` | 索羅輕甲 (1420017) | `DongwuOdyssey.Mod.equipment_1420017.dll` | 自訂屬性 | `mods/equipment_defs.py` |
| `equipment_1510003` | 西北望 (1510003) | `DongwuOdyssey.Mod.equipment_1510003.dll` | 自訂屬性 + 神威詞條（含文案） | `mods/equipment_defs.py`、`mods/mod_texts.py` |
| `equipment_1510099` | 卡西娜德之劍 (1510099) | `DongwuOdyssey.Mod.equipment_1510099.dll` | 傳奇武器數值 + 圖示（含文案） | `mods/equipment_kaxinade_defs.py`、`mods/mod_texts.py` |
| `equipment_1430003` | 大世界法典 (1430003) | `DongwuOdyssey.Mod.equipment_1430003.dll` | 自訂屬性 | `mods/equipment_defs.py` |
| `equipment_1430013` | 巨蜥骨飾 (1430013) | `DongwuOdyssey.Mod.equipment_1430013.dll` | 自訂屬性 | `mods/equipment_defs.py` |
| `equipment_1430021` | 蠻野口籠 (1430021) | `DongwuOdyssey.Mod.equipment_1430021.dll` | 自訂屬性 | `mods/equipment_defs.py` |
| `equipment_1520002` | 柔光紗衣 (1520002) | `DongwuOdyssey.Mod.equipment_1520002.dll` | 自訂 effect／屬性 | `mods/equipment_defs.py` |
| `equipment_1430008` | 名伶殘羽 (1430008) | `DongwuOdyssey.Mod.equipment_1430008.dll` | 自訂屬性 | `mods/equipment_defs.py` |

以上資料 mod 資料夾內皆另有 `DongwuOdyssey.ModCore.dll` 與 `dongwu-data-mod.txt`（`data_combined` 的 txt 內容為 `*`）。

---

## 玩家安裝（Release）

1. 下載 [bepinex-mod-rv0](https://github.com/pullum327/dongwu-odyssey-mod/releases/tag/bepinex-mod-rv0) 三個 zip。
2. 關閉遊戲。
3. 安裝 **BepInEx** → 解壓到遊戲根目錄。
4. 安裝 **plugins** → 複製到 `BepInEx\plugins\`（可只複製需要的 mod 資料夾）。
5. 若使用資料 mod → 覆蓋 **patched-data** 內的 `AnimOdyssey_Data\...`。
6. 使用資料 mod 時建議保留 `dongwu_data_core/`。
7. 啟動遊戲，檢查 `BepInEx\LogOutput.log`。

只裝火煉範例：

```
BepInEx/plugins/
  ignite_no_consume/
  ignite_changming_triple/
  ignite_changming_data/    ← 可選，長明權重
```

---

## 開發者

### 建置與部署

```powershell
cd DongwuOdyssey.BepInEx
.\generate_plugins.ps1
.\build_all.ps1 -Deploy
```

`-Deploy` 會編譯 DLL、部署到 `BepInEx\plugins\`，並呼叫 `apply_mods.py` 合併資料 mod。

### 本機改 mod

```powershell
cd "C:\Program Files (x86)\Steam\steamapps\common\Dongwu Odyssey"
python _ignite_mod\apply_mods.py --list
python _ignite_mod\apply_mods.py --only gacha_xijin_pool
python _ignite_mod\apply_mods.py --restore
```

改卡池：編輯 `mods/gacha_defs.py` 後執行 `--only gacha_xijin_pool`（或重新 `build_all.ps1 -Deploy` 合併全部已部署的資料 mod）。

### 目錄說明

| 路徑 | 用途 |
|------|------|
| `apply_mods.py` | 合併資料 mod 入口 |
| `mod_registry.py` | mod 清單與登錄 |
| `game_data.py` | 讀寫 `game_data.ab` |
| `mods/*.py` | 各 mod 邏輯 |
| `all_items.json` | 查物品／裝備 ID |
| `DongwuOdyssey.BepInEx/` | BepInEx 插件原始碼與 `plugins.json` |

新增資料 mod：在 `mod_registry.py` 與 `DongwuOdyssey.BepInEx/plugins.json` 登記 → `generate_plugins.ps1` → 實作 `mods/` → `build_all.ps1 -Deploy`。

---

## 還原原版

- 資料檔：Steam 驗證遊戲完整性，或 `python _ignite_mod\apply_mods.py --restore`（需有 `.ignite_mod.bak`）。
- 火煉 Harmony：移除對應插件資料夾即可，無需還原 `GameAssembly.dll`。
