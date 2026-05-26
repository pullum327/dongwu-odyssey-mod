using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1410009;

[BepInPlugin("pullum.dongwu.equipment_1410009", "Dongwu: 八十弦月夜花霧", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 八十弦月夜花霧 loaded");
    }
}