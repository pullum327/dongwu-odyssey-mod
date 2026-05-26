using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.HarmonyLib;
using HarmonyLib;

namespace DongwuOdyssey.Mod.ignite_changming_triple;

[BepInPlugin("pullum.dongwu.ignite_changming_triple", "Dongwu: 火煉長明×3", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        var harmony = new Harmony("pullum.dongwu.ignite_changming_triple");
        IgniteChangmingPatches.Apply(harmony, Log);
        Log.LogInfo("Dongwu: 火煉長明×3 loaded");
    }
}