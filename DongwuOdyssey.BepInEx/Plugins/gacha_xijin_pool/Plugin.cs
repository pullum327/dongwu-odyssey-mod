using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.gacha_xijin_pool;

[BepInPlugin("pullum.dongwu.gacha_xijin_pool", "Dongwu: 希金卡池", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 希金卡池 loaded");
    }
}