using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;

namespace DongwuOdyssey.HarmonyLib;

public static class PatchTargets
{
    public const string LocalServer = "Ogopogo.LocalServer";
    public const string UIEquipmentIgnite = "Ogopogo.UI.UIEquipmentIgnite";

    public static Type? TryType(string typeName)
    {
        var type = AccessTools.TypeByName(typeName);
        if (type != null)
            return type;

        var nestedName = typeName.Replace('.', '+');
        type = AccessTools.TypeByName(nestedName);
        if (type != null)
            return type;

        var dot = typeName.LastIndexOf('.');
        if (dot > 0)
        {
            var outer = TryType(typeName[..dot]) ?? AccessTools.TypeByName(typeName[..dot]);
            if (outer != null)
            {
                type = outer.GetNestedType(typeName[(dot + 1)..], BindingFlags.Public | BindingFlags.NonPublic);
                if (type != null)
                    return type;
            }
        }

        foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
        {
            if (asm.GetName().Name?.Contains("Assembly-CSharp", StringComparison.OrdinalIgnoreCase) != true)
                continue;
            type = asm.GetType(typeName) ?? asm.GetType(nestedName);
            if (type != null)
                return type;
        }

        return null;
    }

    public static MethodInfo RequireMethod(string typeName, string methodName, Type[]? parameters = null) =>
        TryMethod(typeName, methodName, parameters)
        ?? throw new InvalidOperationException($"找不到方法: {typeName}.{methodName}");

    public static MethodInfo? TryMethod(string typeName, string methodName, Type[]? parameters = null)
    {
        var type = TryType(typeName);
        if (type == null)
            return null;
        if (parameters != null)
            return AccessTools.Method(type, methodName, parameters);
        return AccessTools.Method(type, methodName)
               ?? AccessTools.GetDeclaredMethods(type).FirstOrDefault(m => m.Name == methodName);
    }
}
