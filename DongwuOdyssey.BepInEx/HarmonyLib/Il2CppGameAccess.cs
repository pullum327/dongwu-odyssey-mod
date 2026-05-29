using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BepInEx.Logging;

namespace DongwuOdyssey.HarmonyLib;

/// <summary>IL2CPP-safe reflection helpers (avoid HarmonyX AmbiguousMatch on overloads / static singletons).</summary>
internal static class Il2CppGameAccess
{
    private const BindingFlags InstanceFlags =
        BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

    private const BindingFlags StaticFlags =
        BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;

    public static object? GetStaticSingleton(string typeName)
    {
        var type = PatchTargets.TryType(typeName);
        if (type == null)
            return null;

        foreach (var field in type.GetFields(StaticFlags))
        {
            if (field.FieldType == type && field.Name is "I" or "Instance")
                return field.GetValue(null);
        }

        foreach (var property in type.GetProperties(StaticFlags))
        {
            if (property.PropertyType != type || property.Name is not ("I" or "Instance"))
                continue;
            if (property.GetIndexParameters().Length != 0)
                continue;
            return property.GetValue(null);
        }

        return null;
    }

    /// <summary>Find instance method by name; never calls Type.GetMethod (IL2CPP overload ambiguity).</summary>
    public static MethodInfo? TryInstanceMethod(
        Type type,
        string methodName,
        int parameterCount = -1,
        params string[] parameterTypeNameHints)
    {
        return type
            .GetMethods(InstanceFlags)
            .FirstOrDefault(m => MatchesMethod(m, methodName, parameterCount, parameterTypeNameHints));
    }

    public static MethodInfo? TryStaticMethod(
        Type type,
        string methodName,
        int parameterCount = -1,
        params string[] parameterTypeNameHints)
    {
        return type
            .GetMethods(StaticFlags)
            .FirstOrDefault(m => MatchesMethod(m, methodName, parameterCount, parameterTypeNameHints));
    }

    private static bool MatchesMethod(
        MethodInfo method,
        string methodName,
        int parameterCount,
        string[] parameterTypeNameHints)
    {
        if (method.Name != methodName)
            return false;
        if (method.IsGenericMethodDefinition || method.ContainsGenericParameters)
            return false;

        var parameters = method.GetParameters();
        if (parameterCount >= 0 && parameters.Length != parameterCount)
            return false;

        if (parameterTypeNameHints.Length == 0)
            return true;

        if (parameters.Length < parameterTypeNameHints.Length)
            return false;

        for (var i = 0; i < parameterTypeNameHints.Length; i++)
        {
            var hint = parameterTypeNameHints[i];
            if (hint.Length == 0)
                continue;

            var paramTypeName = parameters[i].ParameterType.FullName ?? parameters[i].ParameterType.Name;
            if (!paramTypeName.Contains(hint, StringComparison.Ordinal))
                return false;
        }

        return true;
    }

    public static string? TryGetStaticString(Type type, string fieldName)
    {
        foreach (var field in type.GetFields(StaticFlags))
        {
            if (!field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase))
                continue;
            try
            {
                var raw = field.GetValue(null);
                return raw switch
                {
                    null => null,
                    string s => s,
                    _ => raw.ToString(),
                };
            }
            catch
            {
                return null;
            }
        }

        foreach (var property in type.GetProperties(StaticFlags))
        {
            if (!property.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase))
                continue;
            if (property.GetIndexParameters().Length != 0)
                continue;
            try
            {
                var raw = property.GetValue(null);
                return raw switch
                {
                    null => null,
                    string s => s,
                    _ => raw.ToString(),
                };
            }
            catch
            {
                return null;
            }
        }

        return null;
    }

    public static int TryGetStaticInt32(Type type, string fieldName, ManualLogSource? log = null)
    {
        foreach (var field in type.GetFields(StaticFlags))
        {
            if (field.Name != fieldName)
                continue;

            try
            {
                var raw = field.GetValue(null);
                if (raw == null)
                    continue;

                var value = Convert.ToInt32(raw);
                log?.LogInfo($"  讀取靜態欄位 {type.Name}.{fieldName} = {value}");
                return value;
            }
            catch (Exception ex)
            {
                log?.LogWarning($"  讀取靜態欄位 {type.Name}.{fieldName} 失敗: {ex.Message}");
            }
        }

        return 0;
    }

    /// <summary>在實例執行時期別上依參數實際型別配對 overload（避免 IL2CPP 參數型別不符）。</summary>
    public static bool TryInvokeInstance(object instance, string methodName, object?[] args)
        => TryInvoke(instance, InstanceFlags, methodName, args, out _);

    /// <summary>在執行時期別上依參數實際型別配對 static overload。</summary>
    public static bool TryInvokeStatic(object holder, string methodName, object?[] args, out object? result)
        => TryInvoke(holder, StaticFlags, methodName, args, out result);

    private static bool TryInvoke(object holder, BindingFlags flags, string methodName, object?[] args, out object? result)
    {
        result = null;
        var isStatic = (flags & BindingFlags.Static) != 0;
        var target = isStatic ? null : holder;
        var type = holder is Type declared ? declared : holder.GetType();

        var candidates = new List<KeyValuePair<MethodInfo, int>>();
        foreach (var method in type.GetMethods(flags))
        {
            if (method.Name != methodName || method.IsGenericMethodDefinition)
                continue;

            var parameters = method.GetParameters();
            if (parameters.Length != args.Length)
                continue;

            var score = ScoreParameterMatch(parameters, args);
            if (score < 0)
                continue;

            candidates.Add(new KeyValuePair<MethodInfo, int>(method, score));
        }

        if (candidates.Count == 0)
            return false;

        foreach (var pair in candidates.OrderByDescending(c => c.Value))
        {
            var method = pair.Key;
            try
            {
                result = method.Invoke(target, args);
                return true;
            }
            catch (TargetException)
            {
                // IL2CPP 常見：宣告型別 overload 與實際參數包裝型別不符，改試下一個候選
            }
            catch (ArgumentException)
            {
            }
        }

        return false;
    }

    private static int ScoreParameterMatch(ParameterInfo[] parameters, object?[] args)
    {
        var score = 0;
        for (var i = 0; i < parameters.Length; i++)
        {
            var arg = args[i];
            if (arg == null)
            {
                score += 1;
                continue;
            }

            var argType = arg.GetType();
            var paramType = parameters[i].ParameterType;
            if (paramType == argType)
            {
                score += 4;
                continue;
            }

            if (paramType.IsAssignableFrom(argType))
            {
                score += 2;
                continue;
            }

            if (paramType == typeof(object) || argType == typeof(object))
            {
                score += 1;
                continue;
            }

            return -1;
        }

        return score;
    }

    /// <summary>Il2Cpp 靜態欄位有時讀不到，改以 ComponentFactory.Create 探測 type id。</summary>
    public static int ProbeComponentTypeId(
        MethodInfo createInt,
        string expectedComponentName,
        ManualLogSource log,
        int minId = 1,
        int maxId = 256)
    {
        for (var id = minId; id <= maxId; id++)
        {
            object? component;
            try
            {
                component = createInt.Invoke(null, new object[] { id });
            }
            catch
            {
                continue;
            }

            if (component == null)
                continue;

            var name = component.GetType().Name ?? "";
            if (!name.Contains(expectedComponentName, StringComparison.Ordinal))
                continue;

            log.LogInfo($"  探測 ComponentFactory.Create({id}) -> {name}");
            return id;
        }

        return 0;
    }
}
