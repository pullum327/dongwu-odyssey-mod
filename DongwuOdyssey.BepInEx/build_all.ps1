#Requires -Version 5.1
param(
    [switch]$BuildAssets,
    [switch]$Deploy
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$GameDir = Split-Path -Parent $Root
$BepPlugins = Join-Path $GameDir "BepInEx\plugins"

& (Join-Path $Root "generate_plugins.ps1")

if ($BuildAssets) {
    Write-Host "BuildAssets is no longer required for composable data mods; skipping bundled asset generation."
}

Write-Host "build ModCore + HarmonyLib"
dotnet build (Join-Path $Root "ModCore\DongwuOdyssey.ModCore.csproj") -c Release -p:GameDir="$GameDir"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
dotnet build (Join-Path $Root "HarmonyLib\DongwuOdyssey.HarmonyLib.csproj") -c Release -p:GameDir="$GameDir"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$projects = Get-ChildItem (Join-Path $Root "Plugins") -Filter "*.csproj" -Recurse
foreach ($proj in $projects) {
    Write-Host "build $($proj.Name)"
    dotnet build $proj.FullName -c Release -p:GameDir="$GameDir"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Deploy) {
    if (Test-Path (Join-Path $BepPlugins "DongwuOdysseyMod")) {
        Remove-Item -Recurse -Force (Join-Path $BepPlugins "DongwuOdysseyMod")
    }
    foreach ($proj in $projects) {
        $dir = $proj.Directory
        $id = $dir.Name
        $asm = [System.IO.Path]::GetFileNameWithoutExtension($proj.Name)
        $out = Join-Path $dir "bin\Release\net6.0"
        $dest = Join-Path $BepPlugins $id
        if (Test-Path $dest) {
            Remove-Item -Recurse -Force $dest
        }
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item -Force (Join-Path $out "$asm.dll") $dest
        $marker = Join-Path $dir "dongwu-data-mod.txt"
        if (Test-Path $marker) {
            Copy-Item -Force $marker $dest
        }
        $modCoreDll = Join-Path $Root "ModCore\bin\Release\net6.0\DongwuOdyssey.ModCore.dll"
        if (Test-Path $modCoreDll) { Copy-Item -Force $modCoreDll $dest }
        $harmonyDll = Join-Path $Root "HarmonyLib\bin\Release\net6.0\DongwuOdyssey.HarmonyLib.dll"
        if ((Test-Path $harmonyDll) -and ($id -match "^ignite_")) {
            Copy-Item -Force $harmonyDll $dest
        }
        Write-Host "deploy -> $dest"
    }

    $pluginConfig = Get-Content (Join-Path $Root "plugins.json") -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($pluginConfig -isnot [System.Array]) {
        $pluginConfig = @($pluginConfig)
    }
    $validDataIds = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $pluginConfig) {
        if ($entry.kind -eq "data" -and $entry.id -ne "data_combined") {
            [void]$validDataIds.Add([string]$entry.id)
        }
    }

    $dataIds = New-Object 'System.Collections.Generic.List[string]'
    $expandedAll = $false
    foreach ($marker in Get-ChildItem $BepPlugins -Filter "dongwu-data-mod.txt" -Recurse) {
        foreach ($line in Get-Content $marker.FullName -Encoding UTF8) {
            $id = $line.Trim().Trim([char]0xFEFF)
            if ($id.Length -eq 0 -or $id.StartsWith("#")) { continue }
            if ($id -eq "*") {
                if (-not $expandedAll) {
                    foreach ($knownId in $validDataIds) { [void]$dataIds.Add($knownId) }
                    $expandedAll = $true
                }
                continue
            }
            if ($validDataIds.Contains($id)) {
                [void]$dataIds.Add($id)
            } else {
                Write-Warning "Skip non-data mod marker '$id' in $($marker.FullName)"
            }
        }
    }

    if ($dataIds.Count -gt 0) {
        $apply = Join-Path $GameDir "_ignite_mod\apply_mods.py"
        if (-not (Test-Path $apply)) {
            throw "Missing apply_mods.py: $apply"
        }

        $only = (($dataIds | Select-Object -Unique) | Sort-Object) -join ","
        Write-Host "apply data mods at deploy time -> $only"
        python $apply --only $only
        if ($LASTEXITCODE -ne 0) {
            py -3 $apply --only $only
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
    }
}

Write-Host "done. Player packages do not require Python at game startup."
