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
- [`套用火煉Mod.bat`](套用火煉Mod.bat) — 只套用兩個火煉 mod（不寫入設定檔）

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

| 分類 | Mod ID | 說明 |
|------|--------|------|
| 火煉 | `ignite_no_consume` | 不消耗材料、可空材料 |
| 火煉 | `ignite_changming_triple` | 4 條長明、正面數值 ×3 |
| 打磨 | `polish_max_level` | 打磨詞條固定滿級 |
| 打磨 | `polish_soul_siphon` | 靈魂虹吸（全部打磨池） |
| 詞條 | `effect_self_heal` | 自愈 7400023 三級強化 |
| 怪物 | `enemy_hp_multiplier` | 強力/Boss 血量 ×2 |
| 卡池 | `gacha_xijin_pool` | 希金交易會池 4 |
| 造型 | `costume_default_models` | 預設課金造型 |
| 裝備 | `equipment_1410009` 等 | 各裝備獨立 mod（`apply_mods.py --list` 查看完整清單） |

執行 `python "_ignite_mod\apply_mods.py" --list` 可查看目前開關狀態。

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
