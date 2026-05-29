using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;

namespace DongwuOdyssey.HarmonyLib;

public static class Il2CppReflection
{
    private const BindingFlags InstanceFlags =
        BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;

    public static object? GetField(object? instance, string fieldName, string? declaredTypeName = null)
    {
        if (instance == null)
            return null;

        foreach (var type in EnumerateTypes(instance, declaredTypeName))
        {
            for (var cur = type; cur != null; cur = cur.BaseType)
            {
                foreach (var field in cur.GetFields(InstanceFlags))
                {
                    if (!field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase))
                        continue;
                    try
                    {
                        return field.GetValue(instance);
                    }
                    catch
                    {
                        // IL2CPP wrapper 可能需改用宣告型別欄位
                    }
                }

                foreach (var property in cur.GetProperties(InstanceFlags))
                {
                    if (!property.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase) || !property.CanRead)
                        continue;
                    try
                    {
                        return property.GetValue(instance);
                    }
                    catch
                    {
                        // ignore
                    }
                }
            }
        }

        return null;
    }

    public static bool GetBoolField(object instance, string fieldName, string? declaredTypeName = null)
    {
        var v = GetField(instance, fieldName, declaredTypeName);
        return v switch
        {
            bool b => b,
            null => false,
            _ => Convert.ToBoolean(v),
        };
    }

    public static int GetInt32Field(object instance, string fieldName, string? declaredTypeName = null)
    {
        var v = GetField(instance, fieldName, declaredTypeName);
        return v switch
        {
            int i => i,
            long l => (int)l,
            null => 0,
            _ => Convert.ToInt32(v),
        };
    }

    public static long GetInt64Field(object instance, string fieldName, string? declaredTypeName = null)
    {
        var v = GetField(instance, fieldName, declaredTypeName);
        return v switch
        {
            long l => l,
            int i => i,
            null => 0L,
            _ => Convert.ToInt64(v),
        };
    }

    private static IEnumerable<Type> EnumerateTypes(object instance, string? declaredTypeName)
    {
        var seen = new HashSet<Type>();
        if (!string.IsNullOrEmpty(declaredTypeName))
        {
            var declared = PatchTargets.TryType(declaredTypeName);
            if (declared != null && seen.Add(declared))
                yield return declared;
        }

        var runtime = instance.GetType();
        if (seen.Add(runtime))
            yield return runtime;
    }

    public static void SetInt64Field(object instance, string fieldName, long value, string? declaredTypeName = null)
    {
        foreach (var type in EnumerateTypes(instance, declaredTypeName))
        {
            for (var cur = type; cur != null; cur = cur.BaseType)
            {
                var field = cur.GetField(fieldName, InstanceFlags);
                if (field == null)
                    continue;
                field.SetValue(instance, field.FieldType == typeof(int) ? (int)value : value);
                return;
            }
        }

        throw new MissingFieldException(instance.GetType().FullName, fieldName);
    }

    public static void SetBoolField(object instance, string fieldName, bool value, string? declaredTypeName = null)
    {
        SetField(instance, fieldName, value, declaredTypeName);
    }

    public static void SetField(object instance, string fieldName, object? value, string? declaredTypeName = null)
    {
        if (!TrySetField(instance, fieldName, value, declaredTypeName))
            throw new MissingFieldException(instance.GetType().FullName, fieldName);
    }

    public static bool TrySetField(object instance, string fieldName, object? value, string? declaredTypeName = null)
    {
        foreach (var type in EnumerateTypes(instance, declaredTypeName))
        {
            for (var cur = type; cur != null; cur = cur.BaseType)
            {
                foreach (var field in cur.GetFields(InstanceFlags))
                {
                    if (!field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase))
                        continue;

                    try
                    {
                        field.SetValue(instance, value);
                        return true;
                    }
                    catch
                    {
                        // IL2CPP 包裝型別欄位可能需改試屬性
                    }
                }

                foreach (var property in cur.GetProperties(InstanceFlags))
                {
                    if (!property.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase) || !property.CanWrite)
                        continue;

                    try
                    {
                        property.SetValue(instance, value);
                        return true;
                    }
                    catch
                    {
                    }
                }
            }
        }

        return false;
    }

    public static bool TrySetBoolField(object instance, string fieldName, bool value, string? declaredTypeName = null)
        => TrySetField(instance, fieldName, value, declaredTypeName);

    public static bool TrySetInt64Field(object instance, string fieldName, long value, string? declaredTypeName = null)
    {
        foreach (var type in EnumerateTypes(instance, declaredTypeName))
        {
            for (var cur = type; cur != null; cur = cur.BaseType)
            {
                foreach (var field in cur.GetFields(InstanceFlags))
                {
                    if (!field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase))
                        continue;

                    try
                    {
                        field.SetValue(instance, field.FieldType == typeof(int) ? (int)value : value);
                        return true;
                    }
                    catch
                    {
                    }
                }

                foreach (var property in cur.GetProperties(InstanceFlags))
                {
                    if (!property.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase) || !property.CanWrite)
                        continue;

                    try
                    {
                        property.SetValue(instance, property.PropertyType == typeof(int) ? (int)value : value);
                        return true;
                    }
                    catch
                    {
                    }
                }
            }
        }

        return false;
    }

    public static int GetListCount(object list)
    {
        var prop = list.GetType().GetProperty("Count", BindingFlags.Instance | BindingFlags.Public);
        return prop != null ? (int)prop.GetValue(list)! : ((ICollection)list).Count;
    }

    public static void SetListItem(object list, int index, long value)
    {
        var setter = list.GetType().GetMethod("set_Item", new[] { typeof(int), typeof(long) })
                     ?? list.GetType().GetMethod("set_Item", new[] { typeof(int), typeof(object) });
        setter?.Invoke(list, new object[] { index, value });
    }

    public static object? GetListItem(object list, int index)
    {
        var getter = list.GetType().GetMethod("get_Item", BindingFlags.Instance | BindingFlags.Public, null, new[] { typeof(int) }, null);
        return getter?.Invoke(list, new object[] { index });
    }
}
