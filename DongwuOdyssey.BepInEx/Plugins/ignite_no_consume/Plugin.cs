using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.HarmonyLib;
using HarmonyLib;

namespace DongwuOdyssey.Mod.ignite_no_consume;

[BepInPlugin("pullum.dongwu.ignite_no_consume", "Dongwu: 火煉不消耗", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        var harmony = new Harmony("pullum.dongwu.ignite_no_consume");
        IgniteNoConsumePatches.Apply(harmony, Log);
        Log.LogInfo("Dongwu: 火煉不消耗 loaded");
    }
}