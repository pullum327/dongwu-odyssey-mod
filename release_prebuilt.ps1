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

$fullNotes = "全 Mod 预修补包（方案 C）。不需 Python。解压后依 INSTALL.md 覆盖到游戏根目录。适用 resourceVersion=$rv。"
$igniteNotes = "仅火炼预修补包（方案 C）。不需 Python。覆盖 GameAssembly.dll 即可。适用 resourceVersion=$rv。"

& $Gh release create $fullTag $fullZip --repo pullum327/dongwu-odyssey-mod --title "Prebuilt Full Mod (rv$rv)" --notes $fullNotes
& $Gh release create $igniteTag $igniteZip --repo pullum327/dongwu-odyssey-mod --title "Prebuilt Ignite Only (rv$rv)" --notes $igniteNotes

Write-Host "Done: $fullTag , $igniteTag"
