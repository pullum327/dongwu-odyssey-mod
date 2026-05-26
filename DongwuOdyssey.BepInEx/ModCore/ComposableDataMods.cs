using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using BepInEx;
using BepInEx.Logging;

namespace DongwuOdyssey.ModCore;

/// <summary>
/// Records installed data mod declarations.
/// The actual game_data.ab merge is performed at build/deploy time so players do not need Python.
/// </summary>
public static class ComposableDataMods
{
    public const string MarkerFileName = "dongwu-data-mod.txt";

    private static readonly object Gate = new();
    private static bool _appliedThisProcess;

    private static readonly string[] AllDataModIds =
    {
        "ignite_changming_data",
        "polish_max_level",
        "polish_soul_siphon",
        "effect_self_heal",
        "equipment_quality5_rules",
        "enemy_hp_multiplier",
        "gacha_xijin_pool",
        "costume_default_models",
        "equipment_1410009",
        "equipment_1530001",
        "equipment_1420017",
        "equipment_1510003",
        "equipment_1510099",
        "equipment_1430003",
        "equipment_1430013",
        "equipment_1430021",
        "equipment_1520002",
        "equipment_1430008",
    };

    public static void ApplyInstalledDataMods(ManualLogSource log)
    {
        lock (Gate)
        {
            if (_appliedThisProcess)
            {
                log.LogInfo("資料 mod 合併已在本次啟動執行，略過重複呼叫");
                return;
            }

            _appliedThisProcess = true;
        }

        var selected = DiscoverInstalledDataMods(Paths.PluginPath).ToArray();
        if (selected.Length == 0)
        {
            log.LogInfo("未偵測到資料 mod 宣告，略過 game_data 合併");
            return;
        }

        var only = string.Join(",", selected);
        log.LogInfo($"偵測到資料 mod：{only}");
        log.LogInfo("資料檔應已在建置/部署階段合併；玩家端不執行 Python。");
    }

    private static IEnumerable<string> DiscoverInstalledDataMods(string pluginsRoot)
    {
        if (!Directory.Exists(pluginsRoot))
            yield break;

        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var marker in Directory.GetFiles(pluginsRoot, MarkerFileName, SearchOption.AllDirectories))
        {
            foreach (var rawLine in File.ReadAllLines(marker, Encoding.UTF8))
            {
                var id = rawLine.Trim();
                if (id.Length == 0 || id.StartsWith("#", StringComparison.Ordinal))
                    continue;

                if (id == "*")
                {
                    foreach (var allId in AllDataModIds)
                    {
                        if (seen.Add(allId))
                            yield return allId;
                    }

                    continue;
                }

                if (AllDataModIds.Contains(id, StringComparer.OrdinalIgnoreCase) && seen.Add(id))
                    yield return id;
            }
        }
    }

}
