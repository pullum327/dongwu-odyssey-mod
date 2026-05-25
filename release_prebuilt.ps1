# Upload prebuilt ZIPs to GitHub Releases (run after build_prebuilt_release.py).
param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$ModRoot = $PSScriptRoot
$Dist = Join-Path $ModRoot "dist"
$Gh = "C:\Program Files\GitHub CLI\gh.exe"

if (-not $SkipBuild) {
    python (Join-Path $ModRoot "build_prebuilt_release.py")
}

$manifest = Get-Content (Join-Path $Dist "manifest.json") -Raw | ConvertFrom-Json
$rv = $manifest.resourceVersion
$fullTag = "prebuilt-full-rv$rv"
$igniteTag = "prebuilt-ignite-rv$rv"
$fullZip = Join-Path $Dist $manifest.fullZip
$igniteZip = Join-Path $Dist $manifest.igniteZip

Set-Location $ModRoot

$fullNotes = @"
## 全 Mod 預修補包（方案 C）

- **適用：** 遊戲 ``resourceVersion = $rv``
- **不需 Python**：解壓後依 ``INSTALL.md`` 覆蓋到遊戲根目錄
- **包含：** 火煉、打磨、裝備、卡池、怪物、造型、詞條等全部 mod

Steam 更新後若失效，請改用工具版 ``_ignite_mod`` 或等待新版 Release。
"@

$igniteNotes = @"
## 僅火煉預修補包（方案 C）

- **適用：** 遊戲 ``resourceVersion = $rv``
- **不需 Python**：覆蓋 ``GameAssembly.dll`` 即可
- **包含：** ``ignite_no_consume`` + ``ignite_changming_triple``

不修改 ``game_data.ab``。Steam 更新後可能失效。
"@

& $Gh release create $fullTag $fullZip --title "Prebuilt Full Mod (rv$rv)" --notes $fullNotes
& $Gh release create $igniteTag $igniteZip --title "Prebuilt Ignite Only (rv$rv)" --notes $igniteNotes

Write-Host "Done: $fullTag , $igniteTag"
