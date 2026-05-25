# 自訂修改指南

本文件說明如何自行調整**卡池**、**火煉**、**裝備**與**自定義打磨** mod。修改後執行 `apply_mods.py` 套用（需先關閉遊戲）。

道具 ID 可查 [`all_items.json`](all_items.json)（格式 `41XXXXXX` = 裝備道具，`XXXXXXX` 後七位常對應 equipment id）。

---

## 一、卡池（Gacha）

**檔案：** [`mods/gacha_defs.py`](mods/gacha_defs.py)  
**Mod ID：** `gacha_xijin_pool`

### 改哪個池？

```python
GACHA_POOL_XIJIN = 4          # gachapool.json 的 pool id
EPIC_RARE_A = 3               # 視為「史詩」的 rare 值
EPIC_RARE_B = 4
```

若要改其他卡池，把 `GACHA_POOL_XIJIN` 改成對應 id，並在 `apply_gacha_xijin_pool` 內用 `pool["gachaName"]` 找到 `gachaitemtab{gachaName}.json`。

### 加入 / 移出特定裝備

```python
XIJIN_EXTRA_EPIC_ITEMS: dict[int, str] = {
    41430013: "巨蜥骨飾",   # key = 道具 itemID
    ...
}

XIJIN_REMOVED_EPIC_ITEMS: dict[int, str] = {
    41410007: "棘刺弓",     # 從池子刪除的 itemID
    ...
}
```

- **加入**：在 `XIJIN_EXTRA_EPIC_ITEMS` 新增一行；若池內尚無該 itemID，會自動建立一筆 `weight=1000` 的條目。
- **移出**：把 itemID 加進 `XIJIN_REMOVED_EPIC_ITEMS`。

### 調整權重邏輯

目前邏輯（`apply_gacha_xijin_pool`）：

| rare | 處理 |
|------|------|
| 3 或 4 | 保留，`weight` / `guaranteeWeight` / `smallGuaranteeWeight` 至少 1000 |
| 其他 | 三項權重歸零（等於抽不到） |

若要「只提高某幾件機率」而非全史詩，可改迴圈：只對指定 `itemID` 設高權重，其餘維持原值或歸零。

```python
item["weight"] = 5000              # 單品權重
item["guaranteeWeight"] = 5000     # 保底池權重
item["smallGuaranteeWeight"] = 5000
```

---

## 二、火煉（Ignite）

火煉分兩個獨立 mod，改 [`patch_ignite.py`](patch_ignite.py)：

| Mod ID | 內容 |
|--------|------|
| `ignite_no_consume` | 不消耗材料、可空火煉 |
| `ignite_changming_triple` | 火種數量 / 類別 / 正面數值倍率 |

> **注意：** 火煉改的是 `GameAssembly.dll`（RVA 位址）。**遊戲更新後 RVA 可能失效**，需用 Il2CppDumper 重新定位函式。

### 未燃火「數量」

`IGNITE_CHANGMING_TRIPLE_PATCHES` → `GetRandomFlameCount`：

```python
bytes([0xB8, 0x04, 0x00, 0x00, 0x00, 0xC3])  # mov eax, 4 ; ret
#                      ^^ 改成 0x06 = 6 條
```

### 火種「類別」（長明 / 詭獄等）

`RandomFlameId_forceChangming_pick` 與 `_add` 兩處：

```python
bytes([0x6A, 0x02, 0x41, 0x5E, 0x90])  # push 2 → flameId=2（長明）
#            ^^ flameId：需對照遊戲內 flame 表或 dump.cs
```

兩處都要改，否則選取與寫入會不一致。

### 正面數值「倍率」

`build_positive_double_stub` 使用 `lea rdi, [rdi+rdi*2]` → **×3**。

| 倍率 | 作法（概念） |
|------|----------------|
| ×2 | 改為 `add rdi, rdi` 或 `shl rdi, 1` |
| ×3 | 現有 `lea rdi, [rdi+rdi*2]` |
| ×4 | 改為 `shl rdi, 2` |

需同步調整 `POSITIVE_DOUBLE_STUB_LEN` 與 `_stub_looks_valid` 的跳轉偏移，建議改完用 `apply_mods.py --only ignite_changming_triple` 測試。

### 不消耗材料

在 `IGNITE_NO_CONSUME_PATCHES` 內，一般不需改；若要還原某項，從 dict 刪除對應 key 並在 `mods_enabled.json` 關閉 `ignite_no_consume`。

---

## 三、裝備數值 / 固有詞條

**檔案：** [`mods/equipment_defs.py`](mods/equipment_defs.py)  
每件裝備對應一個 `apply_equipment_*` 函式與 `mod_registry.py` 裡的 `equipment_XXXXXXX` mod。

### 固有屬性 `fixAttribute`

格式：`"屬性代碼_數值"`

- **整數型**（如威力、最大生命、速度）：直接填數字，例如 `"101_8"` = 威力 +8。
- **比例型**（如命中、暴擊、抗性）：填小數，例如 `"102_0.2"` = 命中 +20%、 `"104_0.3"` = 暴擊 +30%。
- 名稱對照遊戲內 `EquipmentProp_describe_*` 文案；代碼來源為 `AttributeType` 列舉（見 `_il2cpp_dump/dump.cs`）。

#### 101–118　攻擊／輸出／破抗

| 代碼 | 含義 | 範例 |
|------|------|------|
| 101 | 威力 | `"101_8"` |
| 102 | 命中 | `"102_0.2"` |
| 103 | 最終傷害 | `"103_0.5"` |
| 104 | 暴擊 | `"104_0.3"` |
| 105 | 暴擊效果 | `"105_0.5"` |
| 106 | 眩暈破抗 | `"106_0.5"` |
| 107 | 流血破抗 | `"107_0.5"` |
| 108 | 腐蝕破抗 | `"108_0.5"` |
| 109 | 減益破抗 | `"109_0.5"` |
| 110 | 位移破抗 | `"110_0.5"` |
| 111 | 最終治療 | `"111_0.5"` |
| 112 | 瘴氣治療 | `"112_0.5"` |
| 113 | 抵禦穿透 | `"113_0.5"` |
| 114 | 威力範圍 | `"114_0.2"` |
| 115 | 全破抗 | `"115_0.5"` |
| 116 | 單體技能威力 | `"116_0.3"` |
| 117 | 群體技能威力 | `"117_0.3"` |
| 118 | 滋養效果 | `"118_0.5"` |

#### 201–213　生存／抗性

| 代碼 | 含義 | 範例 |
|------|------|------|
| 201 | 最大生命值 | `"201_15"` |
| 202 | 閃避 | `"202_0.15"` |
| 203 | 抵禦 | `"203_0.5"` |
| 204 | 超越概率 | `"204_0.1"` |
| 205 | 眩暈抗性 | `"205_0.5"` |
| 206 | 流血抗性 | `"206_0.5"` |
| 207 | 腐蝕抗性 | `"207_0.5"` |
| 208 | 減益抗性 | `"208_0.5"` |
| 209 | 位移抗性 | `"209_0.5"` |
| 210 | 瘴氣易傷 | `"210_0.5"` |
| 211 | 受到瘴氣治療 | `"211_0.5"` |
| 212 | 被暴擊率 | `"212_0.3"` |
| 213 | 全抗性 | `"213_0.5"` |

#### 301–304　速度／意志

| 代碼 | 含義 | 範例 |
|------|------|------|
| 301 | 速度 | `"301_6"` |
| 302 | 堅強意志 | `"302_5"` |
| 303 | 受到滋養效果 | `"303_0.5"` |
| 304 | 受到最終治療 | `"304_0.5"` |

#### 401–406　持續傷害／特殊

| 代碼 | 含義 | 範例 |
|------|------|------|
| 401 | 瘴氣傷害 | `"401_0.5"` |
| 402 | 流血傷害 | `"402_0.5"` |
| 403 | 腐蝕傷害 | `"403_0.5"` |
| 404 | 流血易傷 | `"404_0.5"` |
| 405 | 腐蝕易傷 | `"405_0.5"` |
| 406 | 反擊＆追擊傷害 | `"406_0.5"` |

負面屬性放 `negativeAttribute`，數值用負號：`"104_-0.3"`（暴擊 −30%）。

### 固有效果 `effectID`

格式：`"效果ID_等級"`，例如 `"7500004_1"` = 追月 1 級（滿級視 effect 的 levelLimit）。

```python
item["effectID"] = ["7500004_1", "7400003_3", "7599002_1"]
item["negativeAttribute"] = []
```

### 新增一件裝備 mod（流程）

1. 在 `equipment_defs.py` 新增 `apply_equipment_新id(session)`。
2. 在 [`mod_registry.py`](mod_registry.py) 的 `ALL_MODS` 加入 `ModSpec(...)`。
3. 在 [`mods_enabled.json`](mods_enabled.json) 加入 `"equipment_新id": true`。
4. 執行 `python apply_mods.py`。

### 自定義詞條（如神威、靈魂虹吸）

需改三處：

1. **`module.json` 邏輯**：在 `modules` 新增 module（`components` = 效果類型，如 1113=最終傷害、1022=吸血、1126=反擊）。
2. **`equipmenteffect.json`**：新增 effect，`Lv1ModuleID` + `Lv1Param1` 對應數值。
3. **文案**：[`mods/mod_texts.py`](mods/mod_texts.py) 加入 `EquipmentEffect_name_XXX` 等鍵。

參考 `apply_equipment_xibeiwang`（神威）與 [`mods/polish_defs.py`](mods/polish_defs.py) 的 `apply_polish_soul_siphon`（靈魂虹吸 + 加入全部打磨池）。

---

## 四、自定義打磨池

**檔案：** [`mods/polish_defs.py`](mods/polish_defs.py)

| Mod | 作用 |
|-----|------|
| `polish_max_level` | 池內 `"效果ID_等級"` 的等級改為該 effect 的 levelLimit |
| `polish_soul_siphon` | 新增 effect 7599003，並在**每個** pool 的 `effect` 陣列加入 `"7599003_1"` |

只加到特定裝備池：改 `apply_polish_soul_siphon`，依 `pool["poolID"]` 或裝備 id 篩選，不要對全部 pool append。

---

## 五、全局詞條效果（非單件裝備）

**檔案：** [`mods/effect_defs.py`](mods/effect_defs.py)  
**Mod ID：** `effect_self_heal`（分類「詞條」，與「打磨」「裝備」分開）

修改既有 `equipmenteffect.json` 中某個 effect 的等級/module，例如自愈 `7400023` 三級：

```python
self_heal["Lv3ModuleID"] = [742301, 742303]
self_heal["Lv3Param1"] = ["12", "-10"]  # 回血12、降10瘴氣
```

新增全局詞條 mod：在 `effect_defs.py` 加函式 → `mod_registry.py` 註冊（category=`詞條`）→ `mods_enabled.json` 開關。

---

## 六、套用與還原

```powershell
# 改完 gacha / 裝備 / 打磨 後（只動 game_data.ab）
python apply_mods.py --only gacha_xijin_pool
python apply_mods.py --only effect_self_heal

# 改完火煉後（動 DLL）
python apply_mods.py --only ignite_changming_triple

# 還原全部
python apply_mods.py --restore
```

`game_data.ab` 類 mod 每次從 `game_data.ab.ignite_mod.bak` 重算；DLL mod 從 `GameAssembly.dll.ignite_mod.bak` 重算，可任意組合開關。
