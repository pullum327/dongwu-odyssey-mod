# 安尼姆Mod — 本機 Mod 修補

修改 `GameAssembly.dll`（IL2CPP）與 `game_data.ab`（資料）。**請先完全關閉遊戲**再套用；Steam 更新遊戲後需重新執行套用。

---

## 套用 Mod 詳細步驟

### 步驟 0：確認環境（首次使用）

1. 已安裝 **Python 3.10+**（[python.org](https://www.python.org/downloads/) 安裝時勾選「Add to PATH」）。
2. 在 PowerShell 或命令提示字元安裝依賴（只需做一次）：

```powershell
pip install pefile keystone-engine UnityPy
```

3. 確認遊戲目錄結構正確（本資料夾應在遊戲根目錄下）：

```
Dongwu Odyssey/
  GameAssembly.dll          ← 會被修補
  AnimOdyssey_Data/
    StreamingAssets/
      Assets/game_data.ab   ← 會被修補
  _ignite_mod/              ← 本 mod 工具
    apply_mods.py
    mods_enabled.json
```

---

### 步驟 1：關閉遊戲

完全退出《東吳大冒險》，確認工作管理員中沒有 `AnimOdyssey.exe` 或相關程序。  
若遊戲仍在執行，`GameAssembly.dll` 可能無法覆寫。

---

### 步驟 2：選擇要啟用的 Mod

用記事本或 VS Code 開啟 [`mods_enabled.json`](mods_enabled.json)：

- `"true"` = 套用此 mod  
- `"false"` = 略過此 mod  

範例（只開火煉與怪物血量，其餘關閉）：

```json
{
  "ignite_no_consume": true,
  "ignite_changming_triple": true,
  "polish_max_level": false,
  "polish_soul_siphon": false,
  "effect_self_heal": false,
  "enemy_hp_multiplier": true,
  ...
}
```

儲存檔案後繼續步驟 3。

也可用指令查看／調整（不必手動編輯 JSON）：

```powershell
cd "C:\Program Files (x86)\Steam\steamapps\common\Dongwu Odyssey"
python "_ignite_mod\apply_mods.py" --list
python "_ignite_mod\apply_mods.py" --disable gacha_xijin_pool --save
python "_ignite_mod\apply_mods.py" --enable polish_soul_siphon --save
```

---

### 步驟 3：執行套用

**方式 A — 雙擊 bat（最簡單）**

在 `_ignite_mod` 資料夾內雙擊：

- [`套用全部Mod.bat`](套用全部Mod.bat) — 套用 `mods_enabled.json` 中所有 `true` 的 mod  

**方式 B — 命令列**

```powershell
cd "C:\Program Files (x86)\Steam\steamapps\common\Dongwu Odyssey"
python "_ignite_mod\apply_mods.py"
```

**方式 C — 單次套用指定 mod（不改 mods_enabled.json）**

```powershell
python "_ignite_mod\apply_mods.py" --only ignite_no_consume,enemy_hp_multiplier
```

---

### 步驟 4：確認輸出

成功時終端機會列出各 mod 的 `[ok]` 訊息，例如：

```
=== 火煉 / 火煉不消耗材料 ===
  [ok]     CheckIgniteEnough @ ...
=== game_data.ab ===
--- 怪物 / 強力怪物 / 首領血量 ×2 ---
  [ok]   enemy_hp_multiplier ...
  [ok]   game_data.ab 已寫入

完成。請重啟遊戲後測試。
```

**首次套用**會自動建立備份（若尚不存在）：

| 備份檔 | 用途 |
|--------|------|
| `GameAssembly.dll.ignite_mod.bak` | 原始 DLL，還原用 |
| `AnimOdyssey_Data/.../game_data.ab.ignite_mod.bak` | 原始資料 bundle |
| `*.json.ignite_mod.bak` | 語系文案備份 |

---

### 步驟 5：若 DLL 寫入失敗

若看到「無法直接寫入 GameAssembly.dll」，代表遊戲仍在佔用檔案。請：

1. 再次確認遊戲已關閉  
2. 手動將遊戲根目錄下的 **`GameAssembly.dll.patched`** 覆蓋為 **`GameAssembly.dll`**

`game_data.ab` 的修補通常仍已成功，重啟遊戲後資料 mod 即可生效。

---

### 步驟 6：啟動遊戲測試

重新啟動遊戲，進入對應功能驗證（火煉、打磨、戰鬥等）。

---

### 還原原版（出問題時）

```powershell
cd "C:\Program Files (x86)\Steam\steamapps\common\Dongwu Odyssey"
python "_ignite_mod\apply_mods.py" --restore
```

或手動覆蓋：

```powershell
Copy-Item -Force "GameAssembly.dll.ignite_mod.bak" "GameAssembly.dll"
```

---

### Steam 更新後

遊戲更新會覆蓋 `GameAssembly.dll` 與 `game_data.ab`，且 **RVA 位址可能改變**（火煉 DLL patch 可能失效）。建議：

1. 刪除或保留舊備份視情況；若 DLL 已更新，可刪除 `GameAssembly.dll.ignite_mod.bak` 讓腳本以新版建立新備份  
2. 重新執行步驟 3 套用 mod  
3. 若火煉異常，需等待 mod 作者更新 `patch_ignite.py` 中的 RVA

---

## Mod 一覽

在 [`mods_enabled.json`](mods_enabled.json) 中設 `true` / `false` 開關各 mod。  
執行 `python "_ignite_mod\apply_mods.py" --list` 可查看目前狀態。

| 分類 | Mod ID | 修改目標 |
|------|--------|----------|
| 火煉 | `ignite_no_consume` | `GameAssembly.dll` |
| 火煉 | `ignite_changming_triple` | `GameAssembly.dll` |
| 打磨 | `polish_max_level` | `game_data.ab` |
| 打磨 | `polish_soul_siphon` | `game_data.ab` + 語系文案 |
| 詞條 | `effect_self_heal` | `game_data.ab` |
| 怪物 | `enemy_hp_multiplier` | `game_data.ab` |
| 卡池 | `gacha_xijin_pool` | `game_data.ab` |
| 造型 | `costume_default_models` | `game_data.ab` + 語系文案 |
| 裝備 | `equipment_XXXXXXX` | `game_data.ab`（部分含語系文案） |

---

### 火煉

#### `ignite_no_consume` — 火煉不消耗材料

修改 `GameAssembly.dll` 中火煉相關函式：

- **略過材料檢查**：UI 不再要求背包內有火煉材料，可「空材料」進行火煉。
- **不消耗裝備**：作為材料的同裝備不會被扣除。
- **不消耗道具**：火煉所需的材料道具不會被扣除。

> 只 patch 火煉流程內的消耗呼叫，不會動全局 `RemoveItem`，避免影響其他道具使用。

#### `ignite_changming_triple` — 火煉長明 ×3 數值

修改 `GameAssembly.dll` 中火煉隨機與數值計算：

- **固定 4 條未燃火**：每次火煉必出 4 條火焰（原版為隨機數量）。
- **全部強制長明**：4 條火種類別皆為「長明」（`flameId=2`）。
- **正面數值 ×3**：長明等正面火種的數值在寫入前乘以 3（例如 +2 變 +6）。

> 遊戲更新後 DLL 位址可能失效，需重新定位 RVA（見 [`patch_ignite.py`](patch_ignite.py)）。

---

### 打磨

#### `polish_max_level` — 打磨詞條固定滿級

掃描 `equipmenteffectpool.json` 中所有打磨池，將每個 `"效果ID_等級"` 的等級改為該效果在 `equipmenteffect.json` 裡的 `levelLimit`（最高可出等級）。  
例如池內原本 `"7400003_1"` 若該效果滿級為 3，會改為 `"7400003_3"`。  
`perfectEffect`（完美打磨）同樣處理。

#### `polish_soul_siphon` — 自定義打磨：靈魂虹吸

新增自定義打磨詞條 **靈魂虹吸**（effect `7599003`），並加入**全部**打磨池：

| 效果 | 數值 |
|------|------|
| 造成傷害時吸血 | 傷害的 **12%** |
| 最終傷害 | **+30%** |

同時寫入中／英／繁簡 UI 文案（`strings.json` 等）。

---

### 詞條

#### `effect_self_heal` — 自愈 3 級強化

強化全局詞條 **自愈**（effect `7400023`）的 **3 級**效果（不限定某件裝備）：

- 恢復 **12** 點生命值
- 恢復 **10** 點瘴氣

---

### 怪物

#### `enemy_hp_multiplier` — 強力怪物 / 首領血量 ×2

修改 `enemy.json` 中符合條件敵人的 `hp` 欄位，乘以 **2**：

| 條件 | 說明 |
|------|------|
| `size = 2` | 強力怪物 |
| `character = 99` | 首領（Boss） |

**不會**修改：木樁、屍體、以及名稱含「木桩／尸体／屍体」等測試用敵人。  
若同一敵人同時符合強力與首領，只乘一次，不會 ×4。

---

### 卡池

#### `gacha_xijin_pool` — 希金交易會卡池

修改 **希金交易會**（GachaPool id = **4**）的抽卡表：

- **只留史詩**：`rare` 為 3 或 4 的項目保留，權重至少 1000；其餘稀有度權重歸零（抽不到）。
- **額外納入** 5 件史詩：巨蜥骨飾、名伶殘羽、索羅輕甲、大世界法典、蠻野口籠。
- **移出** 22 件原版史詩（棘刺弓、大鱉骨甲、將軍佩劍等，完整清單見 [`mods/gacha_defs.py`](mods/gacha_defs.py)）。

---

### 造型

#### `costume_default_models` — 角色預設課金造型

將指定角色的預設 `model` 改為課金造型外觀（不需解鎖即可看到模型）：

| 角色 ID | 造型模型 |
|---------|----------|
| `100004` | `Al_FoxGarcia002` |
| `100005` | `Al_RabbitSyakuyaku002` |

同時調整角色造型相關 UI 文案（解鎖／替換提示等）。

---

### 裝備

每件裝備為獨立 mod，只改該裝備在 `equipment.json` 的 `fixAttribute`、`effectID`、`negativeAttribute`。  
屬性代碼對照見 [`CUSTOMIZATION.md`](CUSTOMIZATION.md#固有屬性-fixattribute)。

#### `equipment_1410009` — 八十弦月夜花霧

| 項目 | 內容 |
|------|------|
| 固有詞條 | `7400021_3` |
| 屬性 | 威力 +7、暴擊率 +30%、命中 +30% |
| 負面 | 無 |

#### `equipment_1530001` — 維利亞舞鞋

| 項目 | 內容 |
|------|------|
| 固有詞條 | `7500001_1`、`7100002_5`、`7400012_3` |
| 屬性 | 速度 +6、暴擊率 +15%、暴擊傷害 +50%、全抗性 +50% |
| 負面 | 無 |

#### `equipment_1420017` — 索羅輕甲

| 項目 | 內容 |
|------|------|
| 固有詞條 | （無額外 effectID） |
| 屬性 | 最大生命 +15、閃避 +15%、全抗性 +50%、速度 +6 |
| 負面 | 無 |

#### `equipment_1510003` — 西北望（含神威）

| 項目 | 內容 |
|------|------|
| 固有詞條 | `7500004_1`（追月）、`7400003_3`、自定義 **神威** `7599002_1` |
| 神威效果 | 反擊＆追擊傷害 +50%、速度 +3 |
| 屬性 | 威力 +8、命中 +20%、速度 +3 |
| 負面 | 暴擊率 −30% |

含神威的中／英／繁簡 UI 文案。

#### `equipment_1430003` — 大世界法典

| 項目 | 內容 |
|------|------|
| 固有詞條 | （無額外 effectID） |
| 屬性 | 威力 +1、最終傷害 +15%、暴擊傷害 +15%、命中 +15% |
| 負面 | 無 |

#### `equipment_1430013` — 巨蜥骨飾

| 項目 | 內容 |
|------|------|
| 固有詞條 | （無額外 effectID） |
| 屬性 | 威力 +1、最終傷害 +50% |
| 負面 | 無 |

#### `equipment_1430021` — 蠻野口籠

| 項目 | 內容 |
|------|------|
| 固有詞條 | （無額外 effectID） |
| 屬性 | 威力 +1、回合外傷害 +50% |
| 負面 | 無 |

#### `equipment_1520002` — 柔光紗衣

| 項目 | 內容 |
|------|------|
| 固有詞條 | `7500009_1`、`7400013_3`、`7100005_5` |
| 屬性 | 最大生命 +15、暴擊率 +15%、最終治療 +50% |
| 負面 | 無 |

#### `equipment_1430008` — 名伶殘羽

| 項目 | 內容 |
|------|------|
| 固有詞條 | （無額外 effectID） |
| 屬性 | 速度 +3、最終治療 +50%、眩暈破抗 +50% |
| 負面 | 無 |

---

## 自行修改數值

卡池、火煉倍率、裝備屬性、自定義打磨詞條等，見 [`CUSTOMIZATION.md`](CUSTOMIZATION.md)。

---

## 目錄結構

```
_ignite_mod/
  apply_mods.py          # 唯一入口
  mods_enabled.json      # mod 開關
  mod_registry.py        # mod 註冊表
  game_data.py           # game_data.ab 工作階段
  patch_ignite.py        # 火煉 DLL patch
  patch_common.py        # DLL 工具
  mods/                  # 各 mod 實作
  CUSTOMIZATION.md       # 自訂修改指南
  套用全部Mod.bat
  套用火煉Mod.bat
```

---

## 風險

修改遊戲二進位可能違反使用者條款；請自行承擔風險並僅用於單機／離線測試。
