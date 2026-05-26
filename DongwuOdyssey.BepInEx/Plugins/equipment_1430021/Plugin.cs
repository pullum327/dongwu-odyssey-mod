using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1430021;

[BepInPlugin("pullum.dongwu.equipment_1430021", "Dongwu: 蠻野口籠", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 蠻野口籠 loaded");
    }
}