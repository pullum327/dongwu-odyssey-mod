using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.effect_self_heal;

[BepInPlugin("pullum.dongwu.effect_self_heal", "Dongwu: 自愈強化", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 自愈強化 loaded");
    }
}