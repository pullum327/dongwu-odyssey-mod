using BepInEx;
using BepInEx.Unity.IL2CPP;
using DongwuOdyssey.ModCore;

namespace DongwuOdyssey.Mod.ignite_changming_data;

[BepInPlugin("pullum.dongwu.ignite_changming_data", "Dongwu: 火煉長明權重", "1.0.0")]
public class Plugin : BasePlugin
{
    public override void Load()
    {
        ComposableDataMods.ApplyInstalledDataMods(Log);
        Log.LogInfo("Dongwu: 火煉長明權重 loaded");
    }
}