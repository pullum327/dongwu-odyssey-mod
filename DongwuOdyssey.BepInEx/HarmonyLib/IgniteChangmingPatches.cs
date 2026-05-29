using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using BepInEx.Logging;
using HarmonyLib;

namespace DongwuOdyssey.HarmonyLib;

public static class IgniteChangmingPatches
{
    private static ManualLogSource? _log;

    [ThreadStatic]
    private static int _roundingTriplesThisFlow;

    [ThreadStatic]
    private static HashSet<object>? _tripledPositiveAttrs;

    public static void Apply(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        _log = log;
        PatchIgniteEquipmentScope(harmony, log);
        PatchRoundingAttributeValue(harmony, log);
        PatchGetRandomFlameCount(harmony, log);
        PatchRandomFlameId(harmony, log);
        PatchIgniteNewTriple(harmony, log);
        PatchIgniteFlameTriple(harmony, log);
        log.LogInfo("火煉長明×3 Harmony 已套用");
    }

    private static void PatchIgniteEquipmentScope(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.RequireMethod(PatchTargets.LocalServer, "IgniteEquipment");
        var prefix = typeof(IgniteChangmingPatches).GetMethod(nameof(IgniteEquipment_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!;
        var postfix = typeof(IgniteChangmingPatches).GetMethod(nameof(IgniteEquipment_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!;
        harmony.Patch(target, prefix: new HarmonyMethod(prefix), postfix: new HarmonyMethod(postfix));
        log.LogInfo("  + LocalServer.IgniteEquipment (Changming scope)");
    }

    private static void IgniteEquipment_Prefix()
    {
        _roundingTriplesThisFlow = 0;
        _tripledPositiveAttrs = new HashSet<object>(ReferenceEqualityComparer.Instance);
        IgniteFlowScope.Enter();
    }

    private static void IgniteEquipment_Postfix() => IgniteFlowScope.Leave();

    private static void PatchRoundingAttributeValue(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.TryMethod(PatchTargets.LocalServer, "RoundingAttributeValue");
        if (target == null)
        {
            log.LogWarning("  - 略過 LocalServer.RoundingAttributeValue（找不到方法）");
            return;
        }

        var postfix = typeof(IgniteChangmingPatches).GetMethod(nameof(RoundingAttributeValue_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!;
        harmony.Patch(target, postfix: new HarmonyMethod(postfix));
        log.LogInfo("  + LocalServer.RoundingAttributeValue");
    }

    private static void RoundingAttributeValue_Postfix(object? __result)
    {
        if (!IgniteFlowScope.Active || __result == null)
            return;

        try
        {
            if (!Il2CppReflection.TryMultiplyEquipmentAttributeValue(__result, 3, out var value, out var tripled))
                return;

            MarkTripled(__result);
            _roundingTriplesThisFlow++;
            _log?.LogInfo($"  + 火煉生成詞條 ×3: {value} -> {tripled}");
        }
        catch (Exception ex)
        {
            _log?.LogWarning($"RoundingAttributeValue_Postfix: {ex.Message}");
        }
    }

    private static void PatchGetRandomFlameCount(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.RequireMethod(PatchTargets.LocalServer, "GetRandomFlameCount");
        harmony.Patch(target, prefix: new HarmonyMethod(typeof(IgniteChangmingPatches).GetMethod(nameof(GetRandomFlameCount_Prefix), BindingFlags.Static | BindingFlags.NonPublic)!));
        log.LogInfo("  + LocalServer.GetRandomFlameCount");
    }

    private static bool GetRandomFlameCount_Prefix(ref int __result) { __result = 4; return false; }

    private static void PatchRandomFlameId(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.RequireMethod(PatchTargets.LocalServer, "RandomFlameId");
        harmony.Patch(target, postfix: new HarmonyMethod(typeof(IgniteChangmingPatches).GetMethod(nameof(RandomFlameId_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!));
        log.LogInfo("  + LocalServer.RandomFlameId");
    }

    private static void RandomFlameId_Postfix(object __result)
    {
        if (__result == null) return;
        const long id = 2L;
        try
        {
            if (__result is IList list)
            {
                for (var i = 0; i < list.Count; i++) list[i] = id;
                return;
            }
            var n = Il2CppReflection.GetListCount(__result);
            for (var i = 0; i < n; i++) Il2CppReflection.SetListItem(__result, i, id);
        }
        catch { /* ignore */ }
    }

    private static void PatchIgniteNewTriple(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.TryMethod(PatchTargets.LocalServer, "IgniteNew");
        if (target == null) return;
        harmony.Patch(target, postfix: new HarmonyMethod(typeof(IgniteChangmingPatches).GetMethod(nameof(IgniteNew_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!));
        log.LogInfo("  + LocalServer.IgniteNew");
    }

    private static void IgniteNew_Postfix(bool __result, object? __1)
    {
        if (__result && __1 != null) TriplePositive(__1);
    }

    private static void PatchIgniteFlameTriple(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        var target = PatchTargets.TryMethod(PatchTargets.LocalServer, "IgniteFlame");
        if (target == null) return;
        harmony.Patch(target, postfix: new HarmonyMethod(typeof(IgniteChangmingPatches).GetMethod(nameof(IgniteFlame_Postfix), BindingFlags.Static | BindingFlags.NonPublic)!));
        log.LogInfo("  + LocalServer.IgniteFlame");
    }

    private static void IgniteFlame_Postfix(object? __0)
    {
        if (__0 != null) TriplePositive(__0);
    }

    private static void TriplePositive(object equipInfo)
    {
        try
        {
            var listObject = Il2CppReflection.GetField(equipInfo, "EnhanceList");
            if (listObject == null)
            {
                _log?.LogWarning("ApplyPositiveTriple: EnhanceList not found");
                return;
            }

            var changed = 0;
            foreach (var enhance in EnumerateItems(listObject))
            {
                if (enhance == null)
                    continue;

                var pos = GetPositiveAttribute(enhance);
                if (pos == null || AlreadyTripled(pos))
                    continue;

                if (!Il2CppReflection.TryMultiplyEquipmentAttributeValue(pos, 3, out var v, out var tripled))
                    continue;

                MarkTripled(pos);
                changed++;
                _log?.LogInfo($"  + 火煉正面詞條 ×3: {v} -> {tripled}");
            }

            if (changed == 0)
                _log?.LogWarning("ApplyPositiveTriple: 沒有找到可套用 ×3 的正面詞條");
        }
        catch (Exception ex)
        {
            _log?.LogWarning($"ApplyPositiveTriple: {ex.Message}");
        }
    }

    private static IEnumerable<object?> EnumerateItems(object listObject)
    {
        if (listObject is IEnumerable enumerable)
        {
            foreach (var item in enumerable)
                yield return item;
            yield break;
        }

        var count = Il2CppReflection.GetListCount(listObject);
        for (var i = 0; i < count; i++)
            yield return Il2CppReflection.GetListItem(listObject, i);
    }

    private static object? GetPositiveAttribute(object enhance)
    {
        return Il2CppReflection.GetField(enhance, "PositiveAttr")
               ?? Il2CppReflection.GetField(enhance, "PositiveAttribute");
    }

    private static bool AlreadyTripled(object attr) =>
        _tripledPositiveAttrs != null && _tripledPositiveAttrs.Contains(attr);

    private static void MarkTripled(object attr)
    {
        _tripledPositiveAttrs ??= new HashSet<object>(ReferenceEqualityComparer.Instance);
        _tripledPositiveAttrs.Add(attr);
    }
}
