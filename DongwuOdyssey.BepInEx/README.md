# 東吳 Odyssey Mod（BepInEx 多插件）

玩家安裝目標：**不用 Python**。玩家只需要 BepInEx 與已建置好的插件/資料檔。

## 玩家安裝

1. 安裝 BepInEx 6 Unity IL2CPP x64。
2. 關閉遊戲。
3. 將發佈包內的 `BepInEx/plugins/<mod_id>/` 複製到遊戲根目錄。
4. 若發佈包包含資料 mod，請一併覆蓋發佈包內的 `AnimOdyssey_Data/StreamingAssets/...` 資料檔。
5. 啟動遊戲，檢查 `BepInEx/LogOutput.log`。

玩家端不需要 `_ignite_mod`、Python、UnityPy，也不需要執行 `apply_mods.py`。

## Mod 類型

| 類型 | 玩家端行為 |
|------|------------|
| Harmony mod | 只靠 BepInEx DLL 生效，例如 `ignite_no_consume`、`ignite_changming_triple` |
| 資料 mod | 資料檔已在建置/部署階段合併；玩家只安裝已打包好的輸出 |
| `dongwu_data_core` | 啟動時記錄已安裝資料 mod，不在玩家端執行 Python |

## 開發者建置

```powershell
cd DongwuOdyssey.BepInEx
.\generate_plugins.ps1
.\build_all.ps1 -Deploy
```

`-Deploy` 會：

1. 產生並編譯所有插件。
2. 部署到 `BepInEx/plugins/`。
3. 在建置者本機呼叫 `_ignite_mod/apply_mods.py` 合併資料 mod。

因此 Python 只屬於開發/建包流程，不屬於玩家安裝需求。

## 目前限制

資料 mod 是在建置/部署階段寫入 `game_data.ab`。若玩家拿到的是已合併資料檔，之後單純移除某個資料 mod 資料夾，不會自動把 `game_data.ab` 還原成未套用狀態。

需要移除資料 mod 時，請提供另一個已重新建置的發佈包，或讓玩家用 Steam 驗證遊戲完整性還原原版資料。

## 火煉 Harmony

火煉邏輯在 `HarmonyLib/IgniteNoConsumePatches.cs` 與 `HarmonyLib/IgniteChangmingPatches.cs`。這兩個功能不再修改 `GameAssembly.dll`。