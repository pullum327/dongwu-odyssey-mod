using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.enemy_hp_multiplier;

[BepInPlugin("pullum.dongwu.enemy_hp_multiplier", "Dongwu: 怪物血量×2", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 怪物血量×2 loaded");
    }
}