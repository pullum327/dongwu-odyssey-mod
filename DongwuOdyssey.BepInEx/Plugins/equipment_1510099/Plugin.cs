using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1510099;

[BepInPlugin("pullum.dongwu.equipment_1510099", "Dongwu: 卡西娜德之劍", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 卡西娜德之劍 loaded");
    }
}