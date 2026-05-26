# 安尼姆 Mod（`_ignite_mod` + BepInEx）

**GitHub：** https://github.com/pullum327/dongwu-odyssey-mod  

**玩家安裝（不需 Python）** — 依需求下載對應 Release：

| 組合 | 連結 |
|------|------|
| 全部 mod | https://github.com/pullum327/dongwu-odyssey-mod/releases/tag/bepinex-all-rv0 |
| 火煉 + 打磨 + 傳奇規則 + 卡池 + 造型 | https://github.com/pullum327/dongwu-odyssey-mod/releases/tag/bepinex-ignite-polish-gacha-costume-rv0 |
| 僅造型 | https://github.com/pullum327/dongwu-odyssey-mod/releases/tag/bepinex-costume-only-rv0 |

本資料夾供**開發者**改數值、選擇要合併哪些資料 mod、建置 BepInEx 插件。玩家只需解壓 Release 內的 zip，不必執行 Python。

---

## 兩種 mod 如何生效

| 類型 | 生效方式 | 開發時改哪裡 | 玩家關閉方式 |
|------|----------|--------------|--------------|
| **Harmony** | 執行期 DLL 掛鉤 | `DongwuOdyssey.BepInEx/HarmonyLib/*.cs` | 刪除 `BepInEx/plugins/<mod_id>/` |
| **資料 mod** | 建包時寫入 `game_data.ab`、語系 JSON 等 | `_ignite_mod/mods/*.py` + `apply_mods.py` | 須用**對應組合**的 `dongwu-patched-data.zip`；只刪插件資料夾**不會**還原資料 |

---

## Mod 一覽（id、功能、檔案、函數）

### BepInEx Harmony（無 Python，不在 `mod_registry.py`）

| mod id | 插件資料夾 | 主要檔案 | 功能 |
|--------|------------|----------|------|
| `ignite_no_consume` | `BepInEx/plugins/ignite_no_consume/` | `HarmonyLib/IgniteNoConsumePatches.cs` | 火煉不消耗材料 |
| `ignite_changming_triple` | `BepInEx/plugins/ignite_changming_triple/` | `HarmonyLib/IgniteChangmingPatches.cs` | 火煉必出長明，長明詞條數值 ×3 |

插件內 DLL：`DongwuOdyssey.Mod.<mod_id>.dll`、`DongwuOdyssey.ModCore.dll`、`DongwuOdyssey.HarmonyLib.dll`（無 `dongwu-data-mod.txt`）。

---

### 資料 mod（Python 合併 + BepInEx 宣告）

登錄處：`mod_registry.py`（`ModSpec.id` ↔ `apply_*` 函數）。  
插件範本：`DongwuOdyssey.BepInEx/plugins.json` → `generate_plugins.ps1` 產生 `Plugins/<mod_id>/`。

| mod id | 顯示名稱 | 功能摘要 | Python 檔 | `apply_*` 函數 | 插件主 DLL |
|--------|----------|----------|-----------|----------------|------------|
| `ignite_changming_data` | 火煉長明（資料層） | 僅長明（flameId=2）有權重，其餘火焰權重歸零 | `mods/ignite_data_defs.py` | `apply_ignite_changming_data` | `DongwuOdyssey.Mod.ignite_changming_data.dll` |
| `polish_max_level` | 打磨詞條固定滿級 | 各打磨池詞條抽到該 effect 的 `levelLimit` | `mods/polish_defs.py` | `apply_polish_max_level` | `DongwuOdyssey.Mod.polish_max_level.dll` |
| `polish_soul_siphon` | 靈魂虹吸 | 新增詞條並加入打磨池 | `mods/polish_defs.py` | `apply_polish_soul_siphon` | `DongwuOdyssey.Mod.polish_soul_siphon.dll` |
| `effect_self_heal` | 自愈 3 級強化 | 強化 effect `7400023` 三級模組 | `mods/effect_defs.py` | `apply_effect_self_heal` | `DongwuOdyssey.Mod.effect_self_heal.dll` |
| `equipment_quality5_rules` | 傳奇規則 | 傳奇多件穿戴、傳奇部位可火煉 | `mods/equipment_rules_defs.py` | `apply_equipment_quality5_rules` | `DongwuOdyssey.Mod.equipment_quality5_rules.dll` |
| `enemy_hp_multiplier` | 怪物血量 ×2 | 強力怪／首領 HP 加倍（略過木桩、屍體等） | `mods/enemy_defs.py` | `apply_enemy_hp_multiplier` | `DongwuOdyssey.Mod.enemy_hp_multiplier.dll` |
| `gacha_xijin_pool` | 希金交易會卡池 | 調整卡池 4 的史詩裝備清單 | `mods/gacha_defs.py` | `apply_gacha_xijin_pool` | `DongwuOdyssey.Mod.gacha_xijin_pool.dll` |
| `costume_default_models` | 預設課金造型 | 改角色預設 `model` | `mods/costume_defs.py` | `apply_costume_default_models` | `DongwuOdyssey.Mod.costume_default_models.dll` |
| `equipment_1410009` | 八十弦月夜花霧 | 裝備 1410009 屬性／effect | `mods/equipment_defs.py` | `apply_equipment_yaso_moonflower` | `DongwuOdyssey.Mod.equipment_1410009.dll` |
| `equipment_1530001` | 維利亞舞鞋 | 裝備 1530001 | `mods/equipment_defs.py` | `apply_equipment_vilia_dance_shoes` | `DongwuOdyssey.Mod.equipment_1530001.dll` |
| `equipment_1420017` | 索羅輕甲 | 裝備 1420017 | `mods/equipment_defs.py` | `apply_equipment_soluo_light_armor` | `DongwuOdyssey.Mod.equipment_1420017.dll` |
| `equipment_1510003` | 西北望（含神威） | 裝備 1510003 + 神威文案 | `mods/equipment_defs.py`、`mods/mod_texts.py` | `apply_equipment_xibeiwang`、`apply_shenwei_texts` | `DongwuOdyssey.Mod.equipment_1510003.dll` |
| `equipment_1510099` | 卡西娜德之劍 | 傳奇武器數值、圖示、文案 | `mods/equipment_kaxinade_defs.py`、`mods/mod_texts.py` | `apply_equipment_kaxinade`、`apply_kaxinade_texts` | `DongwuOdyssey.Mod.equipment_1510099.dll` |
| `equipment_1430003` | 大世界法典 | 裝備 1430003 | `mods/equipment_defs.py` | `apply_equipment_world_codex` | `DongwuOdyssey.Mod.equipment_1430003.dll` |
| `equipment_1430013` | 巨蜥骨飾 | 裝備 1430013 | `mods/equipment_defs.py` | `apply_equipment_giant_lizard_bone` | `DongwuOdyssey.Mod.equipment_1430013.dll` |
| `equipment_1430021` | 蠻野口籠 | 裝備 1430021 | `mods/equipment_defs.py` | `apply_equipment_savage_muzzle` | `DongwuOdyssey.Mod.equipment_1430021.dll` |
| `equipment_1520002` | 柔光紗衣 | 裝備 1520002 | `mods/equipment_defs.py` | `apply_equipment_soft_light_robe` | `DongwuOdyssey.Mod.equipment_1520002.dll` |
| `equipment_1430008` | 名伶殘羽 | 裝備 1430008 | `mods/equipment_defs.py` | `apply_equipment_actor_feather` | `DongwuOdyssey.Mod.equipment_1430008.dll` |

**文案 mod（不單獨登錄，跟著上表自動執行）**

| 觸發的 mod id | 函數 | 檔案 |
|---------------|------|------|
| `polish_soul_siphon` | `apply_soul_siphon_texts` | `mods/mod_texts.py` |
| `costume_default_models` | `apply_costume_texts` | `mods/mod_texts.py` |
| `equipment_1510003` | `apply_shenwei_texts` | `mods/mod_texts.py` |
| `equipment_1510099` | `apply_kaxinade_texts` | `mods/mod_texts.py` |

**建包用宣告（非 `mod_registry`）**

| mod id | 說明 |
|--------|------|
| `dongwu_data_core` | 掃描 `dongwu-data-mod.txt`，寫 log；建議永遠保留 |
| `data_combined` | `dongwu-data-mod.txt` 內容為 `*` → Deploy 時等同啟用全部資料 mod |

每個資料 mod 插件資料夾另有：`DongwuOdyssey.ModCore.dll`、`dongwu-data-mod.txt`（一行 mod id，或 `data_combined` 為 `*`）。

---

## `mods_enabled.json` 與 `apply_mods.py` 的關係

**結論先講：**

| 操作 | 是否讀 `mods_enabled.json` | 說明 |
|------|---------------------------|------|
| `python apply_mods.py`（無參數） | **是** | 先載入 json，再合併所有 `true` 的資料 mod |
| `python apply_mods.py --only a,b` | **否**（此次覆蓋） | 只套用列出的 id；**預設不寫回** json |
| `python apply_mods.py --only a,b --save` | 寫回 json | 把「只開 a,b」存進 json |
| `python apply_mods.py --enable` / `--disable` | 讀取後寫回 | 更新 json |
| `build_all.ps1 -Deploy` | **否** | 只看 `BepInEx/plugins/**/dongwu-data-mod.txt` 決定 `--only` 清單 |

`mods_enabled.json` 裡的 `ignite_no_consume`、`ignite_changming_triple` **只供對照**（提醒要裝 BepInEx 插件）；`apply_mods.py` 不會用 Python 套用這兩項。  
未出現在 json 的資料 mod id，會以 `mod_registry.py` 的 `DEFAULT_ENABLED`（預設全開）補上。

---

## 選擇要部署哪些 mod（完整流程）

開發時常同時處理三件事：**(A) 合併哪些資料進遊戲檔**、**(B) 磁碟上留哪些 BepInEx 插件資料夾**、**(C) 改 mod 數值**。A 與 B 可以不同步，下面分兩條路說明。

### 流程一：只在本機測資料（最快，不管 BepInEx 插件目錄）

適合：改 `mods/*.py` 後立刻進遊戲看 `game_data.ab` 效果。

1. **選 mod** — 編輯 `_ignite_mod/mods_enabled.json`，把不要的 mod 設為 `false`；或：
   ```powershell
   cd "C:\Program Files (x86)\Steam\steamapps\common\Dongwu Odyssey"
   python _ignite_mod\apply_mods.py --list
   python _ignite_mod\apply_mods.py --disable equipment_1410009,enemy_hp_multiplier
   python _ignite_mod\apply_mods.py --enable gacha_xijin_pool
   ```
2. **合併** — 依 json 一次套用：
   ```powershell
   python _ignite_mod\apply_mods.py
   ```
   或只測單一 mod（**不改 json**）：
   ```powershell
   python _ignite_mod\apply_mods.py --restore
   python _ignite_mod\apply_mods.py --only gacha_xijin_pool
   ```
3. **進遊戲** — 直接啟動；不必先 `build_all.ps1`（Harmony mod 仍需對應插件資料夾在 `BepInEx/plugins/`）。

若要讓 `--only` 的選擇變成預設，加上 `--save`：

```powershell
python _ignite_mod\apply_mods.py --only polish_max_level,gacha_xijin_pool --save
```

---

### 流程二：正式建置並部署到 `BepInEx/plugins`（與 Release 一致）

適合：準備發佈、或本機要與玩家相同的「插件 + 資料檔」組合。

1. **決定要開哪些 mod**（資料 + Harmony 清單）。
2. **調整插件目錄** — 在 `BepInEx/plugins/` 只保留要的資料夾；不要的整夾刪除。  
   - 資料 mod：資料夾內需有 `dongwu-data-mod.txt`，內容一行對應 **mod id**（與上表相同）。  
   - 全開資料 mod：保留 `data_combined/`，其 `dongwu-data-mod.txt` 為 `*`。  
   - Harmony：保留 `ignite_no_consume/`、`ignite_changming_triple/` 等。  
   - 建議永遠保留 `dongwu_data_core/`。
3. **建置與合併**：
   ```powershell
   cd DongwuOdyssey.BepInEx
   .\generate_plugins.ps1    # 依 plugins.json 產生/更新 Plugins 專案（新 mod 時必跑）
   .\build_all.ps1 -Deploy
   ```
   `-Deploy` 會：
   - 編譯並複製 DLL 到 `BepInEx/plugins/<mod_id>/`
   - 掃描各 `dongwu-data-mod.txt` → 組出 id 清單 → 自動執行  
     `python _ignite_mod\apply_mods.py --only <掃到的 id>`
4. **驗證** — 看終端機的 `apply data mods at deploy time -> ...` 是否與預期一致；進遊戲查 `BepInEx/LogOutput.log`。

**注意：** 此流程**不讀** `mods_enabled.json`。若只改了 json 卻沒跑 `apply_mods.py` 或 `-Deploy`，遊戲資料不會變。

---

### 流程對照（避免搞混）

```
mods_enabled.json  ──►  apply_mods.py（無 --only）  ──►  game_data.ab / 語系檔
                              ▲
                              │ 僅此次，不讀 json
BepInEx/plugins/*/dongwu-data-mod.txt  ──►  build_all.ps1 -Deploy  ──►  apply_mods.py --only ...
```

| 你想做的事 | 建議做法 |
|------------|----------|
| 改卡池後只測卡池 | 編輯 `mods/gacha_defs.py` → `apply_mods.py --only gacha_xijin_pool` |
| 改卡池並更新「預設開關」 | 同上，必要時 `--save` 或手動改 `mods_enabled.json` |
| 建置「只含卡池+火煉」的插件包 | 刪減 `BepInEx/plugins/` 資料夾 → `build_all.ps1 -Deploy` |
| 發 GitHub 組合包 | `DongwuOdyssey.BepInEx\publish_release_combos.ps1`（見該目錄 `publish_release_combos.json`） |

---

## 自訂 mod：改哪個 py、常數與函數、之後跑什麼

原則：**改 `mods/` 內對應檔案** → 用 **`apply_mods.py --only <mod_id>`** 寫入遊戲；若已用流程二部署插件，改完後再跑一次 **`build_all.ps1 -Deploy`**（或至少 `--only` 與 Deploy 掃到的 id 一致）。

### 依 mod id 對照

| mod id | 編輯檔案 | 主要可調常數／區塊 | 註冊函數（`mod_registry.py`） |
|--------|----------|-------------------|--------------------------------|
| `ignite_changming_data` | `mods/ignite_data_defs.py` | `CHANGMING_FLAME_ID`、`weight` 邏輯 | `apply_ignite_changming_data` |
| `polish_max_level` | `mods/polish_defs.py` | `apply_polish_max_level` 內池子走訪邏輯 | `apply_polish_max_level` |
| `polish_soul_siphon` | `mods/polish_defs.py`、`mods/mod_texts.py` | `SOUL_SIPHON_EFFECT_ID`、`SOUL_SIPHON_MODULES`、文案 dict | `apply_polish_soul_siphon` |
| `effect_self_heal` | `mods/effect_defs.py` | `SELF_HEAL_EFFECT_ID`、`SELF_HEAL_MIASMA_MODULE_ID`、Lv3 欄位 | `apply_effect_self_heal` |
| `equipment_quality5_rules` | `mods/equipment_rules_defs.py` | `LEGENDARY_SUM_LIMIT_KEY`、`PART_IGNITE_TAGS` | `apply_equipment_quality5_rules` |
| `enemy_hp_multiplier` | `mods/enemy_defs.py` | `ENEMY_HP_MULTIPLIER`、`STRONG_ENEMY_SIZE`、`BOSS_CHARACTER_TYPE` | `apply_enemy_hp_multiplier` |
| `gacha_xijin_pool` | `mods/gacha_defs.py` | `GACHA_POOL_XIJIN`、`XIJIN_EXTRA_EPIC_ITEMS`、`XIJIN_REMOVED_EPIC_ITEMS` | `apply_gacha_xijin_pool` |
| `costume_default_models` | `mods/costume_defs.py`、`mods/mod_texts.py` | `DEFAULT_MODEL_REPLACEMENTS`（角色 id → model 名） | `apply_costume_default_models` |
| `equipment_1410009` | `mods/equipment_defs.py` | `YASO_MOONFLOWER_ID`、`effectID` / `fixAttribute` | `apply_equipment_yaso_moonflower` |
| `equipment_1530001` | 同上 | `VILIA_DANCE_SHOES_ID`、屬性字串 | `apply_equipment_vilia_dance_shoes` |
| `equipment_1420017` | 同上 | `apply_equipment_soluo_light_armor` 內常數 | `apply_equipment_soluo_light_armor` |
| `equipment_1510003` | 同上 + `mod_texts.py` | `apply_equipment_xibeiwang`、神威文案 | `apply_equipment_xibeiwang` |
| `equipment_1510099` | `equipment_kaxinade_defs.py`、`mod_texts.py` | 武器數值、圖示路徑 | `apply_equipment_kaxinade` |
| `equipment_1430003` … `1430008` | `equipment_defs.py` | 各函數開頭的 `*_ID` 與 `item[...]` 指派 | 見 `mod_registry.py` 對應 `apply_equipment_*` |

**查裝備／物品 id：** `all_items.json` 或遊戲資料表；卡池物品 id 為 gacha 表用的 41xxxxxx 形式（見 `gacha_defs.py` 註解）。

**Harmony（火煉不扣料、長明×3）：** 改 `DongwuOdyssey.BepInEx/HarmonyLib/*.cs`，然後 `build_all.ps1 -Deploy`，與 `mods_enabled.json` 無關。

### 範例：改希金卡池

1. 編輯 `mods/gacha_defs.py` 的 `XIJIN_EXTRA_EPIC_ITEMS` / `XIJIN_REMOVED_EPIC_ITEMS`。
2. 套用：
   ```powershell
   python _ignite_mod\apply_mods.py --restore
   python _ignite_mod\apply_mods.py --only gacha_xijin_pool
   ```
3. 若 `BepInEx/plugins/` 裡有 `gacha_xijin_pool/`，建置部署：
   ```powershell
   cd DongwuOdyssey.BepInEx
   .\build_all.ps1 -Deploy
   ```

### 新增一個資料 mod

1. 在 `mods/` 實作 `apply_xxx(session)`。  
2. 在 `mod_registry.py` 的 `ALL_MODS` 新增 `ModSpec(...)`。  
3. 在 `DongwuOdyssey.BepInEx/plugins.json` 新增一筆 `"kind": "data"`。  
4. `.\generate_plugins.ps1` → `.\build_all.ps1 -Deploy`。  
5. 視需要把 id 加入 `mods_enabled.json` 並設為 `true`。

---

## 玩家安裝（Release）

每個 Release 含：`BepInEx-Unity-IL2CPP-*.zip`、`dongwu-bepinex-plugins.zip`、`dongwu-patched-data.zip`、`INSTALL.md`。

1. 關閉遊戲。  
2. BepInEx zip → 遊戲根目錄。  
3. plugins zip → `BepInEx\plugins\`（整包已篩好 mod，勿與**其他 Release** 的 patched-data 混用）。  
4. patched-data zip → `AnimOdyssey_Data\StreamingAssets\`（路徑依 zip 內層目錄覆蓋）。  
5. 啟動遊戲，檢查 `BepInEx/LogOutput.log`。

---

## 目錄說明

| 路徑 | 用途 |
|------|------|
| `apply_mods.py` | 合併資料 mod；讀 `mods_enabled.json`（無 `--only` 時） |
| `mods_enabled.json` | 本機「預設啟用哪些資料 mod」；**Deploy 不讀此檔** |
| `mod_registry.py` | mod id、分類、`apply_*` 對照 |
| `game_data.py` | 讀寫 `game_data.ab` |
| `patch_common.py` | 路徑、備份、還原 |
| `mods/*.py` | 各 mod 邏輯與常數 |
| `all_items.json` | 查物品名稱與 id |
| `DongwuOdyssey.BepInEx/` | BepInEx 原始碼、`plugins.json`、`build_all.ps1`、`publish_release_combos.ps1` |

---

## 還原原版

- **資料檔：** `python _ignite_mod\apply_mods.py --restore`（需有 `.ignite_mod.bak`），或 Steam「驗證遊戲檔案完整性」。  
- **Harmony：** 刪除 `BepInEx/plugins/ignite_no_consume/`、`ignite_changming_triple/` 即可。
