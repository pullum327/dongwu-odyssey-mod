## 全部 Mod（Harmony + 全部資料 mod）

含：火煉、打磨、傳奇規則、卡池、造型、全部裝備 mod、怪物血量、自愈、卡西娜德螺旋追斬（再動）等。

### 安裝（玩家，不需 Python）

1. 關閉遊戲
2. 解壓 `BepInEx-Unity-IL2CPP-*.zip` 到遊戲根目錄（與 `AnimOdyssey.exe` 同層）
3. 解壓 `dongwu-bepinex-plugins.zip`，將內容複製到 `BepInEx\plugins\`
4. 解壓 `dongwu-patched-data.zip`，依 zip 內路徑覆蓋 `AnimOdyssey_Data\StreamingAssets\`
5. 啟動遊戲，檢查 `BepInEx\LogOutput.log`

勿混用**其他 Release** 的 plugins 與 patched-data。

### Steam 遊戲更新後

Steam 更新會還原 `game_data.ab` 等原版檔。請關閉遊戲後，重新下載**同 tag、同 rv** 的 `dongwu-patched-data.zip` 並覆蓋步驟 4 的路徑；或刪除 `game_data.ab.ignite_mod.bak` 後由開發者執行 `build_all.ps1 -Deploy`。詳見倉庫 `_ignite_mod/README.md`「Steam 遊戲更新後」。

### 開發者建置（可選）

1. 解壓 `dongwu-mod-build-source.zip` 到遊戲根目錄（合併 `_ignite_mod` 與 `DongwuOdyssey.BepInEx`）
2. 安裝 .NET 6 SDK、Python 3 + `pip install UnityPy`
3. `cd DongwuOdyssey.BepInEx` → `.\build_all.ps1 -Deploy`
