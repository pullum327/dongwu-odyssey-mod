using System;
using System.Collections;
using System.Reflection;

namespace DongwuOdyssey.HarmonyLib;

public static class Il2CppReflection
{
    public static object? GetField(object? instance, string fieldName)
    {
        if (instance == null)
            return null;
        var field = instance.GetType().GetField(fieldName, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        if (field != null)
            return field.GetValue(instance);

        var property = instance.GetType().GetProperty(fieldName, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        return property?.GetValue(instance);
    }

    public static long GetInt64Field(object instance, string fieldName)
    {
        var v = GetField(instance, fieldName);
        return v switch
        {
            long l => l,
            int i => i,
            null => 0L,
            _ => Convert.ToInt64(v),
        };
    }

    public static void SetInt64Field(object instance, string fieldName, long value)
    {
        var field = instance.GetType().GetField(fieldName, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        if (field != null)
        {
            field.SetValue(instance, field.FieldType == typeof(int) ? (int)value : value);
            return;
        }

        var property = instance.GetType().GetProperty(fieldName, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
        if (property != null)
        {
            property.SetValue(instance, property.PropertyType == typeof(int) ? (int)value : value);
            return;
        }

        throw new MissingFieldException(instance.GetType().FullName, fieldName);
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
