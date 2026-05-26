using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.equipment_1430013;

[BepInPlugin("pullum.dongwu.equipment_1430013", "Dongwu: 巨蜥骨飾", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 巨蜥骨飾 loaded");
    }
}