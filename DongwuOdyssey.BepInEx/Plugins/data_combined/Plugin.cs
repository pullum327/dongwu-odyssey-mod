using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.data_combined;

[BepInPlugin("pullum.dongwu.data_combined", "Dongwu: 全部資料Mod", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 全部資料Mod loaded");
    }
}