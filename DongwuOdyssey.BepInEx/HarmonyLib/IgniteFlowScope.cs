using System;

namespace DongwuOdyssey.HarmonyLib;

internal static class IgniteFlowScope
{
    [ThreadStatic]
    private static int _depth;

    public static bool Active => _depth > 0;
    public static void Enter() => _depth++;
    public static void Leave() { if (_depth > 0) _depth--; }
}
