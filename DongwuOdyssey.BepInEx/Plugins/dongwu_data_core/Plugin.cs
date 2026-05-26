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