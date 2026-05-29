using System;
using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.HarmonyLib;
using DongwuOdyssey.ModCore;
using HarmonyLib;

namespace DongwuOdyssey.Mod.equipment_1510099;

[BepInPlugin("pullum.dongwu.equipment_1510099", "Dongwu: 卡西娜德之劍", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        var harmony = new Harmony("pullum.dongwu.equipment_1510099");
        try
        {
            KaxinadeSpiralStrikePatches.Apply(harmony, Log);
        }
        catch (Exception ex)
        {
            Log.LogError($"Harmony load failed (game continues): {ex}");
        }

        Log.LogInfo("Dongwu: 卡西娜德之劍 loaded");
    }
}