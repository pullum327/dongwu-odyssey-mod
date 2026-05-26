using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1530001;

[BepInPlugin("pullum.dongwu.equipment_1530001", "Dongwu: 維利亞舞鞋", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 維利亞舞鞋 loaded");
    }
}