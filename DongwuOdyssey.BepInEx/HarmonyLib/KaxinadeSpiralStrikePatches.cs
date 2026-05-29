using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using BepInEx.Logging;
using HarmonyLib;

namespace DongwuOdyssey.HarmonyLib;

/// <summary>卡西娜德之劍「螺旋追斬」：單體傷害技結束後再動一次，再動期間自身傷害 -50%。</summary>
public static class KaxinadeSpiralStrikePatches
{
    public const long KaxinadeEquipmentId = 1510099;
    public const long SpiralStrikeEffectId = 7599004;
    public const long SpiralMarkBuffId = 7599010;
    public const long SpiralWeakenBuffId = 7599011;

    private const string BattleLogicType = "Ogopogo.BattleLogic";
    private const string BattleDataActorType = "Ogopogo.BattleDataActor";
    private const string CharacterActorType = "Ogopogo.CharacterActor";
    private const string BuffTypeName = "Ogopogo.Buff";
    private const string ActionContextType = "Ogopogo.ActionContext";
    private const string GameDataType = "Ogopogo.GameData";
    private const string SkillDataType = "Ogopogo.GameData+SkillData";
    private const string StackArgsType = "Ogopogo.StackArgs";
    private const string DamageInfoType = "Ogopogo.DamageInfo";
    private const string SkillInputArgsType = "Ogopogo.SkillInputArgs";
    private const string CalculateDamageArgsType = "Ogopogo.CalculateDamageArgs";

    private const int ActionFlagSkill = 2;

    private static readonly string[] SkillTableNameCandidates = { "SkillsTable", "skills" };
    private static readonly HashSet<int> SingleTargetCastTypes = new() { 0, 3, 4, 5, 6, 9, 12 };
    private static readonly HashSet<int> AoeCastTypes = new() { 1, 2, 7, 8, 10, 11, 13, 14, 15, 16, 17 };

    private static ManualLogSource? _log;
    private static MethodInfo? _isDamageSkill;
    private static MethodInfo? _isTargetEnemyAoe;
    private static MethodInfo? _isTargetAllyAoe;
    private static MethodInfo? _hasBuffByIdLong;
    private static MethodInfo? _hasBuffByIdInt;
    private static MethodInfo? _addBuff;
    private static MethodInfo? _buffCreate;
    private static MethodInfo? _gameDataGetSkill;
    private static MethodInfo? _gameDataGetObject;
    private static object? _gameDataInstance;
    private static string? _skillsTableName;
    private static int _skipLogBudget = 30;

    private sealed class PendingSpiralTurn
    {
        public long AttackerId;
        public long SkillId;
        public object StackArgs = null!;
    }

    [ThreadStatic]
    private static PendingSpiralTurn? _pendingTurn;

    public static void Apply(global::HarmonyLib.Harmony harmony, ManualLogSource log)
    {
        _log = log;
        if (!CacheReflection(log))
        {
            log.LogError("螺旋追斬：反射初始化失敗，略過 Harmony 掛鉤");
            return;
        }

        var doHpSettle = PatchTargets.RequireMethod("Ogopogo.ApplyDamageComponent", "DoHpSettle");
        var doHpPostfix = typeof(KaxinadeSpiralStrikePatches).GetMethod(
            nameof(DoHpSettle_Postfix),
            BindingFlags.Static | BindingFlags.NonPublic)!;
        harmony.Patch(doHpSettle, postfix: new HarmonyMethod(doHpPostfix));
        log.LogInfo("  + ApplyDamageComponent.DoHpSettle (螺旋追斬候選)");

        var onActionOver = PatchTargets.TryMethod(BattleLogicType, "OnDoActionOverStack");
        if (onActionOver != null)
        {
            var actionOverPostfix = typeof(KaxinadeSpiralStrikePatches).GetMethod(
                nameof(OnDoActionOverStack_Postfix),
                BindingFlags.Static | BindingFlags.NonPublic)!;
            harmony.Patch(onActionOver, postfix: new HarmonyMethod(actionOverPostfix));
            log.LogInfo("  + BattleLogic.OnDoActionOverStack postfix (再動 + 自傷減半 debuff)");
        }
        else
        {
            log.LogWarning("  - 找不到 BattleLogic.OnDoActionOverStack");
        }

        log.LogInfo("螺旋追斬（再動）Harmony 已套用");
    }

    private static bool CacheReflection(ManualLogSource log)
    {
        try
        {
            var skillDataType = PatchTargets.TryType(SkillDataType);
            if (skillDataType != null)
            {
                _isDamageSkill = skillDataType.GetMethod("IsDamageSkill", BindingFlags.Instance | BindingFlags.Public);
                _isTargetEnemyAoe = skillDataType.GetMethod("IsTargetEnemyAoe", BindingFlags.Instance | BindingFlags.Public);
                _isTargetAllyAoe = skillDataType.GetMethod("IsTargetAllyAoe", BindingFlags.Instance | BindingFlags.Public);
            }

            var characterType = PatchTargets.TryType(CharacterActorType);
            if (characterType != null)
            {
                _hasBuffByIdLong = Il2CppGameAccess.TryInstanceMethod(characterType, "HasBuff", parameterCount: 1, "Int64");
                _hasBuffByIdInt = Il2CppGameAccess.TryInstanceMethod(characterType, "HasBuff", parameterCount: 1, "Int32");
                _addBuff = Il2CppGameAccess.TryInstanceMethod(characterType, "AddBuff", parameterCount: 2)
                           ?? Il2CppGameAccess.TryInstanceMethod(characterType, "AddBuff", parameterCount: 3);
            }

            var buffType = PatchTargets.TryType(BuffTypeName);
            if (buffType != null)
            {
                _buffCreate = buffType
                    .GetMethods(BindingFlags.Static | BindingFlags.Public)
                    .FirstOrDefault(m => m.Name == "Create" && m.GetParameters().Length >= 4);
            }

            var gameDataType = PatchTargets.TryType(GameDataType);
            if (gameDataType != null)
            {
                foreach (var method in gameDataType.GetMethods(BindingFlags.Static | BindingFlags.Public))
                {
                    if (method.Name != "Get" || !method.IsGenericMethodDefinition)
                        continue;
                    var parameters = method.GetParameters();
                    if (parameters.Length != 2)
                        continue;
                    if (parameters[1].ParameterType == typeof(long))
                    {
                        _gameDataGetSkill = method;
                        break;
                    }
                }

                _gameDataGetObject = Il2CppGameAccess.TryInstanceMethod(gameDataType, "Get", parameterCount: 2, "String", "Int64")
                                     ?? Il2CppGameAccess.TryInstanceMethod(gameDataType, "Get", parameterCount: 2);
                _gameDataInstance = Il2CppGameAccess.GetStaticSingleton(GameDataType);
            }

            if (_isDamageSkill == null)
                log.LogWarning("  - 找不到 IsDamageSkill");
            if (_buffCreate == null)
                log.LogWarning("  - 找不到 Buff.Create");
            if (_addBuff == null)
                log.LogWarning("  - 找不到 CharacterActor.AddBuff");

            return _isDamageSkill != null && _buffCreate != null && _addBuff != null;
        }
        catch (Exception ex)
        {
            log.LogError($"螺旋追斬反射快取失敗: {ex.Message}");
            return false;
        }
    }

    private static void DoHpSettle_Postfix(
        object? __instance,
        object? actor,
        object? context,
        object? stackArgs,
        int i,
        object? beAttackInfo)
    {
        _ = __instance;
        _ = actor;
        _ = i;
        _ = beAttackInfo;

        if (context == null || stackArgs == null)
            return;

        if (!TryValidateSpiralStrike(stackArgs, beAttackInfo, context, out var attackerId, out var skillId, out _))
            return;

        _pendingTurn = new PendingSpiralTurn
        {
            AttackerId = attackerId,
            SkillId = skillId,
            StackArgs = stackArgs,
        };
    }

    private static void OnDoActionOverStack_Postfix(object? __instance, object? bda, object? context)
    {
        var pending = _pendingTurn;
        _pendingTurn = null;

        if (pending == null || bda == null || context == null)
            return;

        if (!IsSkillActionContext(context))
            return;

        var battleLogic = __instance ?? Il2CppGameAccess.GetStaticSingleton(BattleLogicType);
        if (battleLogic == null)
            return;

        var attacker = FindCharacterActor(battleLogic, pending.AttackerId, context);
        if (attacker == null)
            return;

        if (!HasKaxinadeSpiral(attacker))
            return;

        if (HasBuffById(attacker, SpiralWeakenBuffId))
        {
            LogSkip(pending.SkillId, "已在螺旋追斬再動中");
            return;
        }

        if (!TryValidateSpiralStrike(pending.StackArgs, null, context, out _, out _, out var failReason))
        {
            LogSkip(pending.SkillId, failReason);
            return;
        }

        var buffOk = TryApplyWeakenBuff(attacker, pending.AttackerId);
        var turnOk = TryGrantExtraTurn(bda, pending.AttackerId);

        _log?.LogInfo(
            $"螺旋追斬再動 attacker={pending.AttackerId} skill={pending.SkillId} debuff={buffOk} extraTurn={turnOk}");
    }

    private static bool IsSkillActionContext(object context)
    {
        var flag = Il2CppReflection.GetField(context, "flag", ActionContextType);
        if (flag is int i)
            return i == ActionFlagSkill;
        if (flag != null && Enum.IsDefined(flag.GetType(), ActionFlagSkill))
            return Convert.ToInt32(flag) == ActionFlagSkill;
        return false;
    }

    private static bool TryApplyWeakenBuff(object attacker, long actorId)
    {
        if (_buffCreate == null || _addBuff == null)
            return false;

        try
        {
            var parameters = _buffCreate.GetParameters();
            var args = new object?[parameters.Length];
            args[0] = SpiralWeakenBuffId;
            args[1] = actorId;
            args[2] = actorId;
            for (var j = 3; j < args.Length; j++)
                args[j] = parameters[j].ParameterType == typeof(bool) ? true : null;

            var buff = _buffCreate.Invoke(null, args);
            if (buff == null)
                return false;

            var addParams = _addBuff.GetParameters();
            if (addParams.Length >= 3)
                return _addBuff.Invoke(attacker, new object?[] { buff, false, actorId }) is true;
            return _addBuff.Invoke(attacker, new object?[] { buff, false }) is true;
        }
        catch (Exception ex)
        {
            _log?.LogWarning($"施加螺旋追斬 debuff 失敗: {ex.GetBaseException().Message}");
            return false;
        }
    }

    private static bool TryGrantExtraTurn(object bda, long actorId)
    {
        var orderObj = Il2CppReflection.GetField(bda, "actionOrder", BattleDataActorType);
        if (orderObj is not IList list || list.Count == 0)
            return false;

        var idx = Il2CppReflection.GetInt32Field(bda, "currentActionIdx", BattleDataActorType);
        var insertAt = Math.Min(Math.Max(idx, 0), list.Count);

        if (!TryFindActionTuple(list, actorId, out var remoteId, out var third))
        {
            if (insertAt > 0 && TryReadActionTuple(list[insertAt - 1]!, out _, out remoteId, out third))
            {
                // 沿用上一筆的 remote / priority
            }
            else
            {
                remoteId = actorId;
                third = 0;
            }
        }

        try
        {
            var tupleType = typeof(Tuple<long, long, long>);
            var entry = Activator.CreateInstance(tupleType, actorId, remoteId, third);
            if (entry == null)
                return false;
            list.Insert(insertAt, entry);
            return true;
        }
        catch (Exception ex)
        {
            _log?.LogWarning($"插入再行動失敗: {ex.GetBaseException().Message}");
            return false;
        }
    }

    private static bool TryFindActionTuple(IList list, long actorId, out long remoteId, out long third)
    {
        remoteId = 0;
        third = 0;
        foreach (var item in list)
        {
            if (item == null)
                continue;
            if (!TryReadActionTuple(item, out var id, out remoteId, out third))
                continue;
            if (id == actorId)
                return true;
        }

        return false;
    }

    private static bool TryReadActionTuple(object tuple, out long actorId, out long remoteId, out long third)
    {
        actorId = 0;
        remoteId = 0;
        third = 0;

        var t = tuple.GetType();
        var p1 = t.GetProperty("Item1") ?? t.GetProperty("m_Item1");
        var p2 = t.GetProperty("Item2") ?? t.GetProperty("m_Item2");
        var p3 = t.GetProperty("Item3") ?? t.GetProperty("m_Item3");
        if (p1 == null)
            return false;

        actorId = Convert.ToInt64(p1.GetValue(tuple));
        if (p2 != null)
            remoteId = Convert.ToInt64(p2.GetValue(tuple));
        if (p3 != null)
            third = Convert.ToInt64(p3.GetValue(tuple));
        return true;
    }

    private static bool TryValidateSpiralStrike(
        object stackArgs,
        object? beAttackInfo,
        object? context,
        out long attackerId,
        out long skillId,
        out string failReason)
    {
        attackerId = 0;
        skillId = 0;
        failReason = "";

        if (!TryResolveAttack(stackArgs, beAttackInfo, out attackerId, out skillId, out var skillData, out failReason))
            return false;

        if (skillData == null || _isDamageSkill == null)
        {
            failReason = "缺少 skillData";
            return false;
        }

        if (_isDamageSkill.Invoke(skillData, null) is not true)
        {
            failReason = "非傷害技能";
            return false;
        }

        var battleLogic = Il2CppGameAccess.GetStaticSingleton(BattleLogicType);
        if (battleLogic == null)
        {
            failReason = "BattleLogic 單例為 null";
            return false;
        }

        var actor = FindCharacterActor(battleLogic, attackerId, context);
        if (actor == null)
        {
            failReason = $"找不到角色 {attackerId}";
            return false;
        }

        if (!HasKaxinadeSpiral(actor))
        {
            failReason = "未裝備卡西娜德之劍或未帶螺旋追斬";
            return false;
        }

        return true;
    }

    private static bool TryResolveAttack(
        object stackArgs,
        object? beAttackInfo,
        out long attackerId,
        out long skillId,
        out object? skillData,
        out string failReason)
    {
        attackerId = 0;
        skillId = 0;
        skillData = null;
        failReason = "";

        if (beAttackInfo != null
            && Il2CppReflection.GetBoolField(beAttackInfo, "isAdditionalAttack", DamageInfoType))
        {
            failReason = "追加攻擊不觸發";
            return false;
        }

        if (beAttackInfo != null)
        {
            skillId = Il2CppReflection.GetInt64Field(beAttackInfo, "skillId", DamageInfoType);
            attackerId = Il2CppReflection.GetInt64Field(beAttackInfo, "damageSrcActorId", DamageInfoType);
        }

        var damageArgs = Il2CppReflection.GetField(stackArgs, "damageArgs", StackArgsType);
        if (damageArgs != null)
        {
            if (attackerId == 0)
                attackerId = Il2CppReflection.GetInt64Field(damageArgs, "attackerId", CalculateDamageArgsType);
            if (skillId == 0)
                skillId = Il2CppReflection.GetInt64Field(damageArgs, "skillId", CalculateDamageArgsType);
        }

        var skillInputArgs = Il2CppReflection.GetField(stackArgs, "skillInputArgs", StackArgsType);
        if (skillInputArgs != null)
        {
            skillData = Il2CppReflection.GetField(skillInputArgs, "skillData", SkillInputArgsType);
            if (attackerId == 0)
                attackerId = Il2CppReflection.GetInt64Field(skillInputArgs, "srcActorId", SkillInputArgsType);
            if (skillId == 0 && skillData != null)
                skillId = Il2CppReflection.GetInt64Field(skillData, "id", SkillDataType);
        }

        if (skillId == 0 || attackerId == 0)
        {
            failReason = $"無法解析攻擊者/技能 (attacker={attackerId} skill={skillId})";
            return false;
        }

        if (skillData == null)
            skillData = TryGetSkillDataById(skillId);

        if (!IsSingleTargetAttack(stackArgs, skillId, skillData, out failReason))
            return false;

        return true;
    }

    private static object? TryGetSkillDataById(long skillId)
    {
        if (_gameDataGetSkill == null && _gameDataGetObject == null)
            return null;

        if (_gameDataInstance == null)
            _gameDataInstance = Il2CppGameAccess.GetStaticSingleton(GameDataType);
        if (_gameDataInstance == null)
            return null;

        foreach (var tableName in EnumerateSkillTableNames())
        {
            try
            {
                object? row = _gameDataGetSkill != null
                    ? _gameDataGetSkill.Invoke(_gameDataInstance, new object[] { tableName, skillId })
                    : _gameDataGetObject!.Invoke(_gameDataInstance, new object[] { tableName, skillId });
                if (row == null)
                    continue;
                _skillsTableName = tableName;
                return row;
            }
            catch
            {
            }
        }

        return null;
    }

    private static IEnumerable<string> EnumerateSkillTableNames()
    {
        if (!string.IsNullOrEmpty(_skillsTableName))
            yield return _skillsTableName;
        foreach (var candidate in SkillTableNameCandidates)
        {
            if (candidate != _skillsTableName)
                yield return candidate;
        }
    }

    private static bool IsSingleTargetAttack(
        object stackArgs,
        long skillId,
        object? skillData,
        out string failReason)
    {
        failReason = "";

        var damageArgs = Il2CppReflection.GetField(stackArgs, "damageArgs", StackArgsType);
        if (damageArgs != null)
        {
            var defenders = Il2CppReflection.GetField(damageArgs, "defenderIds", CalculateDamageArgsType);
            var defenderCount = defenders == null ? 0 : Il2CppReflection.GetListCount(defenders);
            if (defenderCount == 1)
                return true;
            if (defenderCount > 1)
            {
                failReason = $"defenderIds={defenderCount}（需 1）";
                return false;
            }
        }

        var skillInputArgs = Il2CppReflection.GetField(stackArgs, "skillInputArgs", StackArgsType);
        if (skillInputArgs != null)
        {
            var targets = Il2CppReflection.GetField(skillInputArgs, "targets", SkillInputArgsType);
            var targetCount = targets == null ? 0 : Il2CppReflection.GetListCount(targets);
            if (targetCount == 1)
                return true;
            if (targetCount > 1)
            {
                failReason = $"targets={targetCount}（需 1）";
                return false;
            }
        }

        skillData ??= TryGetSkillDataById(skillId);
        if (skillData != null)
        {
            var castType = Il2CppReflection.GetInt32Field(skillData, "castType", SkillDataType);
            if (AoeCastTypes.Contains(castType))
            {
                failReason = $"AOE castType={castType}";
                return false;
            }

            if (SingleTargetCastTypes.Contains(castType))
                return true;

            if (_isTargetEnemyAoe != null && _isTargetAllyAoe != null)
            {
                if (_isTargetEnemyAoe.Invoke(skillData, null) is true || _isTargetAllyAoe.Invoke(skillData, null) is true)
                {
                    failReason = "AOE 技能";
                    return false;
                }

                return true;
            }
        }

        failReason = skillData == null ? "無法載入 SkillData" : "無法判定單體目標";
        return false;
    }

    private static bool HasKaxinadeSpiral(object characterActor)
    {
        if (HasBuffById(characterActor, SpiralMarkBuffId))
            return true;

        if (GetWeaponEquipmentId(characterActor) == KaxinadeEquipmentId)
            return true;

        var equipments = Il2CppReflection.GetField(characterActor, "equipments");
        if (equipments is IEnumerable equipmentList)
        {
            foreach (var equipment in equipmentList)
            {
                if (equipment != null && Il2CppReflection.GetInt64Field(equipment, "equipmentID") == KaxinadeEquipmentId)
                    return true;
            }
        }

        var effects = Il2CppReflection.GetField(characterActor, "equipmentResultEffect");
        if (effects is IDictionary dict)
        {
            foreach (DictionaryEntry entry in dict)
            {
                if (entry.Key is long id && id == SpiralStrikeEffectId)
                    return true;
                if (entry.Key is int iid && iid == SpiralStrikeEffectId)
                    return true;
            }
        }

        return false;
    }

    private static bool HasBuffById(object characterActor, long buffId)
    {
        if (_hasBuffByIdLong != null && _hasBuffByIdLong.Invoke(characterActor, new object[] { buffId }) is true)
            return true;
        if (_hasBuffByIdInt != null && buffId <= int.MaxValue
            && _hasBuffByIdInt.Invoke(characterActor, new object[] { (int)buffId }) is true)
            return true;
        return false;
    }

    private static long GetWeaponEquipmentId(object characterActor)
    {
        var weapon = Il2CppReflection.GetField(characterActor, "weapon");
        return weapon == null ? 0 : Il2CppReflection.GetInt64Field(weapon, "equipmentID");
    }

    private static object? FindCharacterActor(object battleLogic, long actorId, object? context)
    {
        _ = context;
        var world = ResolveGameWorld(battleLogic);
        if (world == null)
            return null;

        return FindActorInWorld(world, actorId, CharacterActorType)
               ?? FindActorInWorld(world, actorId, null);
    }

    private static object? ResolveGameWorld(object battleLogic)
    {
        var world = Il2CppReflection.GetField(battleLogic, "world", BattleLogicType);
        if (world != null)
            return world;

        var gameWorldType = PatchTargets.TryType("Ogopogo.GameWorld");
        if (gameWorldType == null)
            return null;

        foreach (var field in gameWorldType.GetFields(BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic))
        {
            if (field.Name != "current" || field.FieldType != gameWorldType)
                continue;
            return field.GetValue(null);
        }

        return null;
    }

    private static object? FindActorInWorld(object world, long actorId, string? declaredActorTypeName)
    {
        var worldType = world.GetType();

        if (!string.IsNullOrEmpty(declaredActorTypeName))
        {
            var actorType = PatchTargets.TryType(declaredActorTypeName);
            var genericFind = worldType
                .GetMethods(BindingFlags.Instance | BindingFlags.Public)
                .FirstOrDefault(m =>
                    m.Name == "FindActorById"
                    && m.IsGenericMethodDefinition
                    && m.GetParameters().Length == 1);
            if (actorType != null && genericFind != null)
            {
                try
                {
                    return genericFind.MakeGenericMethod(actorType).Invoke(world, new object[] { actorId });
                }
                catch
                {
                }
            }
        }

        var find = Il2CppGameAccess.TryInstanceMethod(worldType, "FindActorById", parameterCount: 1, "Int64");
        return find?.Invoke(world, new object[] { actorId });
    }

    private static void LogSkip(long skillId, string failReason)
    {
        if (_log == null)
            return;

        if (skillId == 10004011 || _skipLogBudget > 0)
        {
            if (skillId != 10004011)
                _skipLogBudget--;
            _log.LogInfo($"螺旋追斬略過 skill={skillId}: {failReason}");
        }
    }
}
