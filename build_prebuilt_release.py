#!/usr/bin/env python3
"""Build pre-patched release ZIPs (Scheme C) for GitHub Releases.

Outputs under _ignite_mod/dist/:
  prebuilt-full-rv{N}.zip
  prebuilt-ignite-rv{N}.zip

Requires: game backups (*.ignite_mod.bak), game closed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAME_ROOT = ROOT.parent
DIST = ROOT / "dist"
APPLY = ROOT / "apply_mods.py"
BUILD_JSON = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets" / "build.json"

FULL_LOCALE_FILES = (
    "AnimOdyssey_Data/StreamingAssets/strings.json",
    "AnimOdyssey_Data/StreamingAssets/Languages/zh-Hant/zh-Hant.json",
    "AnimOdyssey_Data/StreamingAssets/Languages/zh-Hans/zh-Hans.json",
    "AnimOdyssey_Data/StreamingAssets/Languages/en-US/en-US.json",
)

FULL_DATA_FILES = (
    "GameAssembly.dll",
    "AnimOdyssey_Data/StreamingAssets/Assets/game_data.ab",
    "AnimOdyssey_Data/StreamingAssets/asset_map.json",
    *FULL_LOCALE_FILES,
)

IGNITE_FILES = ("GameAssembly.dll",)


def _run_apply(*args: str) -> None:
    cmd = [sys.executable, str(APPLY), *args]
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=GAME_ROOT, check=True)


def _resource_version() -> int:
    if BUILD_JSON.exists():
        return int(json.loads(BUILD_JSON.read_text(encoding="utf-8")).get("resourceVersion", 1))
    return 1


def _copy_files(staging: Path, rel_paths: tuple[str, ...]) -> None:
    for rel in rel_paths:
        src = GAME_ROOT / rel
        dst = staging / rel
        if not src.exists():
            raise SystemExit(f"缺少檔案：{src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  [copy] {rel}")


def _write_install(staging: Path, variant: str, rv: int) -> None:
    if variant == "full":
        body = f"""# 預修補 Mod 安裝說明（全 Mod 版）

**適用遊戲 resourceVersion：** {rv}  
**內容：** 全部 mod（火煉、打磨、裝備、卡池、怪物、造型、詞條等）

## 步驟

1. **完全關閉**《東吳大冒險》。
2. 若尚未備份，請先複製以下原版檔案到其他資料夾：
   - `GameAssembly.dll`
   - `AnimOdyssey_Data/StreamingAssets/Assets/game_data.ab`
   - `AnimOdyssey_Data/StreamingAssets/asset_map.json`
   - 語系 JSON（若存在 `.ignite_mod.bak` 可略過）
3. 將本 ZIP 內檔案**依相同路徑**覆蓋到遊戲根目錄，例如：
   ```
   C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dongwu Odyssey\\
   ```
4. 啟動遊戲測試。

## 還原原版

用 Steam「驗證遊戲檔案完整性」，或還原你自行備份的原版檔案。

## 注意

- **不需安裝 Python**。
- Steam 更新遊戲後本包可能失效，請等待對應新版本 Release。
- 修改遊戲檔案請自行承擔風險。
"""
    else:
        body = f"""# 預修補 Mod 安裝說明（僅火煉版）

**適用遊戲 resourceVersion：** {rv}  
**內容：** 僅火煉 mod（不消耗材料 + 4 條長明 ×3 數值）

## 步驟

1. **完全關閉**《東吳大冒險》。
2. 建議先備份原版 `GameAssembly.dll`。
3. 將 ZIP 內的 `GameAssembly.dll` 覆蓋到遊戲根目錄：
   ```
   C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dongwu Odyssey\\GameAssembly.dll
   ```
4. 啟動遊戲，測試火煉功能。

## 還原原版

Steam「驗證遊戲檔案完整性」，或還原備份的 `GameAssembly.dll`。

## 注意

- **不需安裝 Python**；不修改 `game_data.ab`。
- 遊戲更新後可能失效，請等待新版 Release。
"""
    (staging / "INSTALL.md").write_text(body, encoding="utf-8")


def _zip_staging(staging: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  [zip] {zip_path.name} ({size_mb:.1f} MB)")


def _all_mod_ids() -> str:
    from mod_registry import ALL_MODS

    return ",".join(mod.id for mod in ALL_MODS)


def build() -> tuple[Path, Path, int]:
    rv = _resource_version()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    print("\n=== 還原原版（自備份） ===")
    _run_apply("--restore")

    print("\n=== 打包：僅火煉 ===")
    _run_apply("--only", "ignite_no_consume,ignite_changming_triple")
    ignite_staging = DIST / "staging-ignite"
    ignite_staging.mkdir()
    _copy_files(ignite_staging, IGNITE_FILES)
    _write_install(ignite_staging, "ignite", rv)
    ignite_zip = DIST / f"prebuilt-ignite-rv{rv}.zip"
    _zip_staging(ignite_staging, ignite_zip)

    print("\n=== 還原後打包：全 Mod ===")
    _run_apply("--restore")
    _run_apply("--only", _all_mod_ids())
    full_staging = DIST / "staging-full"
    full_staging.mkdir()
    _copy_files(full_staging, FULL_DATA_FILES)
    _write_install(full_staging, "full", rv)
    full_zip = DIST / f"prebuilt-full-rv{rv}.zip"
    _zip_staging(full_staging, full_zip)

    print("\n=== 還原遊戲目錄（建包完成） ===")
    _run_apply("--restore")

    manifest = {
        "resourceVersion": rv,
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "fullZip": full_zip.name,
        "igniteZip": ignite_zip.name,
        "suggestedTags": {
            "full": f"prebuilt-full-rv{rv}",
            "ignite": f"prebuilt-ignite-rv{rv}",
        },
    }
    (DIST / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return full_zip, ignite_zip, rv


if __name__ == "__main__":
    build()
