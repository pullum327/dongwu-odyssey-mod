using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.polish_soul_siphon;

[BepInPlugin("pullum.dongwu.polish_soul_siphon", "Dongwu: 靈魂虹吸", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 靈魂虹吸 loaded");
    }
}