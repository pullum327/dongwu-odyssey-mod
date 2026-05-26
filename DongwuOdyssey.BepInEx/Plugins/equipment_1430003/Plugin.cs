using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1430003;

[BepInPlugin("pullum.dongwu.equipment_1430003", "Dongwu: 大世界法典", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 大世界法典 loaded");
    }
}