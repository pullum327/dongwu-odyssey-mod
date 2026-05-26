#Requires -Version 5.1
# Build combo-specific GitHub Release zips (plugins + patched-data + BepInEx).
param(
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"
$GameDir = Split-Path -Parent $PSScriptRoot
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

function Publish-GhRelease($combo, $bepZip, $pluginsZip, $dataZip, $notesFile) {
    $repo = "pullum327/dongwu-odyssey-mod"
    $tag = $combo.Tag
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    gh release view $tag --repo $repo 2>$null | Out-Null
    $exists = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEap
    if ($exists) {
        Write-Host "release exists, upload assets: $tag"
        gh release upload $tag $bepZip $pluginsZip $dataZip $notesFile --repo $repo --clobber
    } else {
        gh release create $tag `
            --repo $repo `
            --title $combo.Title `
            --notes-file $notesFile `
            $bepZip $pluginsZip $dataZip $notesFile
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
    Set-Content -Path (Join-Path $outDir "INSTALL.md") -Encoding UTF8 -Value $combo.Notes

    Write-Host "built $($combo.Tag)"
    if (-not $SkipUpload) {
        Publish-GhRelease $combo $bepZip $pluginsZip $dataZip (Join-Path $outDir "INSTALL.md")
    }
}

Write-Host "done. dist -> $DistRoot"
