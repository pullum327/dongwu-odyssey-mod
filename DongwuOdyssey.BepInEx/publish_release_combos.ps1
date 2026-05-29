#Requires -Version 5.1
# Build combo-specific GitHub Release zips (plugins + patched-data + BepInEx).
param(
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"

function Resolve-GameDirFromScript([string]$bepInExRoot) {
    $parent = Split-Path -Parent $bepInExRoot
    if (Test-Path (Join-Path $parent "AnimOdyssey.exe")) { return $parent }
    $grand = Split-Path -Parent $parent
    if (Test-Path (Join-Path $grand "AnimOdyssey.exe")) { return $grand }
    throw "無法判定遊戲根目錄：請在含 AnimOdyssey.exe 的目錄下執行（遊戲根或 _ignite_mod 內的 DongwuOdyssey.BepInEx）"
}

function Resolve-BepInExSourceRoot([string]$GameDir) {
    foreach ($p in @(
            (Join-Path $GameDir "DongwuOdyssey.BepInEx"),
            (Join-Path $GameDir "_ignite_mod\DongwuOdyssey.BepInEx")
        )) {
        if (Test-Path (Join-Path $p "build_all.ps1")) { return $p }
    }
    throw "找不到 DongwuOdyssey.BepInEx（需含 build_all.ps1）"
}

function Copy-TreeExcluding([string]$src, [string]$dest, [string[]]$excludeDirNames) {
    if (-not (Test-Path $src)) { throw "缺少來源: $src" }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $excludeSet = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($n in $excludeDirNames) { [void]$excludeSet.Add($n) }
    foreach ($item in Get-ChildItem $src -Force) {
        if ($item.PSIsContainer) {
            if ($excludeSet.Contains($item.Name)) { continue }
            Copy-TreeExcluding $item.FullName (Join-Path $dest $item.Name) $excludeDirNames
        } else {
            if ($item.Extension -eq ".bak") { continue }
            Copy-Item -Force $item.FullName (Join-Path $dest $item.Name)
        }
    }
}

function Copy-BuildSourceStaging([string]$destRoot, [string]$GameDir) {
    $igniteSrc = Join-Path $GameDir "_ignite_mod"
    if (-not (Test-Path (Join-Path $igniteSrc "apply_mods.py"))) {
        throw "缺少 _ignite_mod\apply_mods.py（遊戲根目錄下需有 _ignite_mod）"
    }
    $bepSrc = Resolve-BepInExSourceRoot $GameDir
    $exclude = @(".git", "dist", "bin", "obj", "__pycache__", ".venv", "venv")
    Copy-TreeExcluding $igniteSrc (Join-Path $destRoot "_ignite_mod") ($exclude + @("DongwuOdyssey.BepInEx"))
    Copy-TreeExcluding $bepSrc (Join-Path $destRoot "DongwuOdyssey.BepInEx") $exclude
    $hint = @"
# dongwu-mod-build-source

解壓到《東吳大冒險》Steam 遊戲根目錄（與 AnimOdyssey.exe 同層）。

需求：.NET 6 SDK、Python 3（pip install UnityPy）

建置並部署到 BepInEx\plugins\、合併 game_data.ab：
  cd DongwuOdyssey.BepInEx
  .\build_all.ps1 -Deploy

Steam 遊戲更新後必做步驟：見 _ignite_mod\README.md「Steam 遊戲更新後」。
"@
    Set-Content -Path (Join-Path $destRoot "BUILD_SOURCE_README.md") -Encoding UTF8 -Value $hint
}

$GameDir = Resolve-GameDirFromScript $PSScriptRoot
$BepPlugins = Join-Path $GameDir "BepInEx\plugins"
$Apply = Join-Path $GameDir "_ignite_mod\apply_mods.py"
$DistRoot = Join-Path $GameDir "_ignite_mod\dist"
$Rv = 0
$buildJson = Join-Path $GameDir "AnimOdyssey_Data\StreamingAssets\build.json"
if (Test-Path $buildJson) {
    $Rv = [int]((Get-Content $buildJson -Raw | ConvertFrom-Json).resourceVersion)
}

$configPath = Join-Path $PSScriptRoot "publish_release_combos.json"
$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$Combos = foreach ($entry in $config.combos) {
    $notesPath = Join-Path $PSScriptRoot $entry.notesFile
    [pscustomobject]@{
        Tag           = "bepinex-$($entry.id)-rv$Rv"
        Title         = "$($entry.title) (rv$Rv)"
        PluginFolders = @($entry.pluginFolders)
        DataOnly      = @($entry.dataOnly)
        Notes         = Get-Content $notesPath -Raw -Encoding UTF8
    }
}

function Copy-PatchedDataStaging($destRoot) {
    $base = Join-Path $destRoot "AnimOdyssey_Data\StreamingAssets"
    $assets = Join-Path $base "Assets"
    New-Item -ItemType Directory -Force -Path $assets | Out-Null
    Copy-Item -Force (Join-Path $GameDir "AnimOdyssey_Data\StreamingAssets\Assets\game_data.ab") (Join-Path $assets "game_data.ab")
    Copy-Item -Force (Join-Path $GameDir "AnimOdyssey_Data\StreamingAssets\asset_map.json") (Join-Path $base "asset_map.json")
    $sprite = Join-Path $GameDir "AnimOdyssey_Data\StreamingAssets\Assets\spriteatlas.ab"
    if (Test-Path $sprite) {
        Copy-Item -Force $sprite (Join-Path $assets "spriteatlas.ab")
    }
    foreach ($rel in @(
        "AnimOdyssey_Data\StreamingAssets\strings.json",
        "AnimOdyssey_Data\StreamingAssets\Languages\zh-Hant\zh-Hant.json",
        "AnimOdyssey_Data\StreamingAssets\Languages\zh-Hans\zh-Hans.json",
        "AnimOdyssey_Data\StreamingAssets\Languages\en-US\en-US.json"
    )) {
        $src = Join-Path $GameDir $rel
        if (Test-Path $src) {
            $d = Join-Path $destRoot (Split-Path $rel -Parent)
            New-Item -ItemType Directory -Force -Path $d | Out-Null
            Copy-Item -Force $src (Join-Path $destRoot $rel)
        }
    }
}

function Invoke-ApplyDataOnly($ids) {
    $only = ($ids | Sort-Object) -join ","
    Write-Host "apply_mods --only $only"
    python $Apply --restore
    if ($LASTEXITCODE -ne 0) { throw "apply_mods --restore failed" }
    python $Apply --only $only
    if ($LASTEXITCODE -ne 0) {
        py -3 $Apply --only $only
        if ($LASTEXITCODE -ne 0) { throw "apply_mods --only failed" }
    }
}

function Publish-GhRelease($combo, $bepZip, $pluginsZip, $dataZip, $sourceZip, $notesFile) {
    $repo = "pullum327/dongwu-odyssey-mod"
    $tag = $combo.Tag
    $assets = @($bepZip, $pluginsZip, $dataZip, $sourceZip, $notesFile)
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    gh release view $tag --repo $repo 2>$null | Out-Null
    $exists = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEap
    if ($exists) {
        Write-Host "release exists, upload assets: $tag"
        gh release upload $tag @assets --repo $repo --clobber
    } else {
        gh release create $tag `
            --repo $repo `
            --title $combo.Title `
            --notes-file $notesFile `
            @assets
    }
    if ($LASTEXITCODE -ne 0) { throw "gh release failed: $tag" }
}

$bepZipSrc = Get-ChildItem $GameDir -File | Where-Object { $_.Name -like "BepInEx-Unity-IL2CPP*.zip" } | Select-Object -First 1
if (-not $bepZipSrc) { throw "找不到 BepInEx 安裝 zip" }

if (Test-Path $DistRoot) { Remove-Item -Recurse -Force $DistRoot }
New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null

Write-Host "combos: $($Combos.Count) -> $(($Combos | ForEach-Object { $_.Tag }) -join ', ')"
foreach ($combo in $Combos) {
    $outDir = Join-Path $DistRoot $combo.Tag
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null

    Invoke-ApplyDataOnly $combo.DataOnly

    $pluginsStage = Join-Path $outDir "plugins-staging"
    New-Item -ItemType Directory -Force -Path $pluginsStage | Out-Null
    foreach ($folder in $combo.PluginFolders) {
        $src = Join-Path $BepPlugins $folder
        if (-not (Test-Path $src)) { throw "缺少插件資料夾: $src" }
        Copy-Item -Recurse -Force $src (Join-Path $pluginsStage $folder)
    }

    $pluginsZip = Join-Path $outDir "dongwu-bepinex-plugins.zip"
    $dataZip = Join-Path $outDir "dongwu-patched-data.zip"
    $bepZip = Join-Path $outDir "BepInEx-Unity-IL2CPP-win-x64-6.0.0-be-725.zip"
    if (Test-Path $pluginsZip) { Remove-Item -Force $pluginsZip }
    if (Test-Path $dataZip) { Remove-Item -Force $dataZip }
    Compress-Archive -Path "$pluginsStage\*" -DestinationPath $pluginsZip -Force
    $dataStage = Join-Path $outDir "data-staging"
    if (Test-Path $dataStage) { Remove-Item -Recurse -Force $dataStage }
    New-Item -ItemType Directory -Force -Path $dataStage | Out-Null
    Copy-PatchedDataStaging $dataStage
    Compress-Archive -Path "$dataStage\*" -DestinationPath $dataZip -Force
    Remove-Item -Recurse -Force $dataStage, $pluginsStage
    Copy-Item -Force $bepZipSrc.FullName $bepZip
    $sourceStage = Join-Path $outDir "source-staging"
    if (Test-Path $sourceStage) { Remove-Item -Recurse -Force $sourceStage }
    New-Item -ItemType Directory -Force -Path $sourceStage | Out-Null
    Copy-BuildSourceStaging $sourceStage $GameDir
    $sourceZip = Join-Path $outDir "dongwu-mod-build-source.zip"
    if (Test-Path $sourceZip) { Remove-Item -Force $sourceZip }
    Compress-Archive -Path "$sourceStage\*" -DestinationPath $sourceZip -Force
    Remove-Item -Recurse -Force $sourceStage
    Set-Content -Path (Join-Path $outDir "INSTALL.md") -Encoding UTF8 -Value $combo.Notes

    Write-Host "built $($combo.Tag) (+ build source)"
    if (-not $SkipUpload) {
        Publish-GhRelease $combo $bepZip $pluginsZip $dataZip $sourceZip (Join-Path $outDir "INSTALL.md")
    }
}

Write-Host "done. dist -> $DistRoot"
