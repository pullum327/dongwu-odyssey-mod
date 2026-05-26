using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.polish_max_level;

[BepInPlugin("pullum.dongwu.polish_max_level", "Dongwu: 打磨滿級", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 打磨滿級 loaded");
    }
}