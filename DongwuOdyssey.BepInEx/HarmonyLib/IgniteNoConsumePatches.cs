using System;
using System.Reflection;
using BepInEx.Logging;
using HarmonyLib;

namespace DongwuOdyssey.HarmonyLib;

public static class IgniteNoConsumePatches
{
    public static void Apply(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        PatchCheckIgniteEnough(harmony, log);
        PatchIgniteEquipment(harmony, log);
        PatchConsumeBypass(harmony, log);
        log.LogInfo("火煉不消耗 Harmony 已套用");
    }

    private static void PatchCheckIgniteEnough(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.TryMethod(PatchTargets.UIEquipmentIgnite, "CheckIgniteEnough")
                     ?? throw new InvalidOperationException("CheckIgniteEnough");
        var prefix = typeof(IgniteNoConsumePatches).GetMethod(nameof(CheckIgniteEnough_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!;
        harmony.Patch(target, prefix: new HarmonyMethod(prefix));
        log.LogInfo("  + UIEquipmentIgnite.CheckIgniteEnough");
    }

    private static bool CheckIgniteEnough_Prefix(object? igniteCtrl, ref bool __result)
    {
        if (igniteCtrl == null) return true;
        __result = true;
        return false;
    }

    private static void PatchIgniteEquipment(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.RequireMethod(PatchTargets.LocalServer, "IgniteEquipment");
        var prefix = typeof(IgniteNoConsumePatches).GetMethod(nameof(IgniteEquipment_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!;
        var postfix = typeof(IgniteNoConsumePatches).GetMethod(nameof(IgniteEquipment_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!;
        harmony.Patch(target, prefix: new HarmonyMethod(prefix), postfix: new HarmonyMethod(postfix));
        log.LogInfo("  + LocalServer.IgniteEquipment");
    }

    private static void IgniteEquipment_Prefix() => IgniteFlowScope.Enter();
    private static void IgniteEquipment_Postfix() => IgniteFlowScope.Leave();

    private static void PatchConsumeBypass(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        foreach (var name in new[] { "RemoveEquipmentByPlayerItemID", "RemoveItems", "RemoveItemFromBag", "RemoveItem", "RemoveItemFromCollection", "RemoveEquipmentItem", "RemovePlayerItem", "SubItems" })
            PatchConsumeMethod(harmony, log, name);
    }

    private static void PatchConsumeMethod(global::HarmonyLib.Harmony harmony, ManualLogSource log, string methodName)
    {
        var method = PatchTargets.TryMethod(PatchTargets.LocalServer, methodName);
        if (method == null) { log.LogWarning($"  - 略過 {methodName}"); return; }
        if (method.ReturnType == typeof(bool))
            harmony.Patch(method, prefix: new HarmonyMethod(typeof(IgniteNoConsumePatches).GetMethod(nameof(ConsumeBool_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!));
        else if (method.ReturnType == typeof(int))
            harmony.Patch(method, prefix: new HarmonyMethod(typeof(IgniteNoConsumePatches).GetMethod(nameof(ConsumeInt_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!));
        log.LogInfo($"  + LocalServer.{methodName}");
    }

    private static bool ConsumeBool_Prefix(ref bool __result)
    {
        if (!IgniteFlowScope.Active) return true;
        __result = true;
        return false;
    }

    private static bool ConsumeInt_Prefix(ref int __result)
    {
        if (!IgniteFlowScope.Active) return true;
        __result = 0;
        return false;
    }
}
