using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_quality5_rules;

[BepInPlugin("pullum.dongwu.equipment_quality5_rules", "Dongwu: 傳奇規則", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 傳奇規則 loaded");
    }
}