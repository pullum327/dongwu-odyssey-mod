using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1510003;

[BepInPlugin("pullum.dongwu.equipment_1510003", "Dongwu: 西北望", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 西北望 loaded");
    }
}