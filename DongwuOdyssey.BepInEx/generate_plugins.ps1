#Requires -Version 5.1
# Generate one BepInEx plugin project per mod (plugins.json).
# Data mods are composable: each folder declares its id and ModCore merges all selected ids once.
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$PluginsRoot = Join-Path $Root "Plugins"
$json = Get-Content (Join-Path $Root "plugins.json") -Raw -Encoding UTF8 | ConvertFrom-Json

function Write-Utf8Bom($path, $text) {
    $utf8Bom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllText($path, $text, $utf8Bom)
}

New-Item -ItemType Directory -Force -Path $PluginsRoot | Out-Null

function Write-DataCoreProject() {
    $id = "dongwu_data_core"
    $dir = Join-Path $PluginsRoot $id
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    $pluginCs = @"
using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.dongwu_data_core;

[BepInPlugin("pullum.dongwu.data_core", "Dongwu: Data Mod Core", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: Data Mod Core loaded");
    }
}
"@

    $csproj = @"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>DongwuOdyssey.Mod.dongwu_data_core</AssemblyName>
    <RootNamespace>DongwuOdyssey.Mod.dongwu_data_core</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\ModCore\DongwuOdyssey.ModCore.csproj" />
    <PackageReference Include="BepInEx.Unity.IL2CPP" Version="6.0.0-be.735" />
    <PackageReference Include="BepInEx.PluginInfoProps" Version="2.1.0" />
  </ItemGroup>
</Project>
"@

    Write-Utf8Bom (Join-Path $dir "Plugin.cs") $pluginCs
    Write-Utf8Bom (Join-Path $dir "DongwuOdyssey.Mod.dongwu_data_core.csproj") $csproj
    Write-Host "generated $id"
}

Write-DataCoreProject

foreach ($p in $json) {
    $id = $p.id
    $safe = $id -replace '[^a-zA-Z0-9_]', '_'
    $dir = Join-Path $PluginsRoot $id
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    $asm = "DongwuOdyssey.Mod.$safe"
    $guid = "pullum.dongwu.$id"
    $displayName = "Dongwu: $($p.name)"

    if ($p.kind -eq "harmony") {
        $applyLine = if ($p.patch -eq "NoConsume") {
            "IgniteNoConsumePatches.Apply(harmony, Log);"
        } else {
            "IgniteChangmingPatches.Apply(harmony, Log);"
        }
        $pluginCs = @"
using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.HarmonyLib;
using HarmonyLib;

namespace $asm;

[BepInPlugin("$guid", "$displayName", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        var harmony = new Harmony("$guid");
        $applyLine
        Log.LogInfo("$displayName loaded");
    }
}
"@
        $refs = @"
  <ItemGroup>
    <ProjectReference Include="..\..\ModCore\DongwuOdyssey.ModCore.csproj" />
    <ProjectReference Include="..\..\HarmonyLib\DongwuOdyssey.HarmonyLib.csproj" />
    <PackageReference Include="BepInEx.Unity.IL2CPP" Version="6.0.0-be.735" />
    <PackageReference Include="BepInEx.PluginInfoProps" Version="2.1.0" />
    <PackageReference Include="HarmonyX" Version="2.10.2" />
  </ItemGroup>
"@
    } else {
        $pluginCs = @"
using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace $asm;

[BepInPlugin("$guid", "$displayName", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("$displayName loaded");
    }
}
"@
        $refs = @"
  <ItemGroup>
    <ProjectReference Include="..\..\ModCore\DongwuOdyssey.ModCore.csproj" />
    <PackageReference Include="BepInEx.Unity.IL2CPP" Version="6.0.0-be.735" />
    <PackageReference Include="BepInEx.PluginInfoProps" Version="2.1.0" />
  </ItemGroup>
"@
    }

    $csproj = @"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>$asm</AssemblyName>
    <RootNamespace>$asm</RootNamespace>
  </PropertyGroup>
$refs
</Project>
"@
    Write-Utf8Bom (Join-Path $dir "Plugin.cs") $pluginCs
    Write-Utf8Bom (Join-Path $dir "$asm.csproj") $csproj
    if ($p.kind -eq "data") {
        $markerValue = if ($id -eq "data_combined") { "*" } else { $id }
        Write-Utf8Bom (Join-Path $dir "dongwu-data-mod.txt") ($markerValue + "`n")
    }
    Write-Host "generated $id"
}

Write-Host "done: $((Get-ChildItem $PluginsRoot -Directory).Count) plugin projects under Plugins/"
