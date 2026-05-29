## 火煉 + 打磨 + 傳奇規則 + 希金卡池 + 預設造型

### 安裝（玩家，不需 Python）

1. 關閉遊戲
2. 解壓 BepInEx zip 到遊戲根目錄
3. 解壓 `dongwu-bepinex-plugins.zip` → `BepInEx\plugins\`
4. 解壓 `dongwu-patched-data.zip` → `AnimOdyssey_Data\StreamingAssets\`
5. 啟動遊戲

勿與其他 Release 的 patched-data 混用。

### Steam 遊戲更新後

重新套用**本 Release** 的 `dongwu-patched-data.zip`（或下載同 rv 的新 Release）。詳見 `_ignite_mod/README.md`「Steam 遊戲更新後」。

### 開發者建置（可選）

解壓 `dongwu-mod-build-source.zip` 到遊戲根目錄後，於 `DongwuOdyssey.BepInEx` 執行 `.\build_all.ps1 -Deploy`（需 .NET 6、Python + UnityPy）。
