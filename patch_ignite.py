#!/usr/bin/env python3
"""
Dongwu Odyssey / AnimOdyssey - Equipment Ignite (火煉) local patches.

- Always roll 4 unburned flames (GetRandomFlameCount -> 4)
- All 4 flame types forced to 長明 (flameId=2) in RandomFlameId
- Positive flame stat values x3 (寫入 [rbx+18] 前 lea rdi,[rdi+rdi*2])
- UI material check always passes (CheckIgniteEnough -> true)
- IgniteEquipment does not consume selected equipment or material items

Note: Do NOT patch RemoveItem globally — it breaks all item use in the game.
"""
from __future__ import annotations

import shutil
import struct
import sys
from pathlib import Path

try:
    import pefile
except ImportError:
    print("Install: pip install pefile")
    sys.exit(1)

from patch_common import (
    DLL,
    make_jmp_rel32,
    patch_bytes,
    place_text_code,
    sha256,
    write_dll,
)

GAME_ROOT = Path(__file__).resolve().parent.parent
BACKUP = GAME_ROOT / "GameAssembly.dll.ignite_mod.bak"

# 唯一寫入正面數值：mov [rbx+18], rdi（RVA 0x9880A0 於 IgniteFlame 內僅此一處）
POSITIVE_DOUBLE_HOOK_RVA = 0x9880A0
POSITIVE_DOUBLE_HOOK_LEN = 7
POSITIVE_DOUBLE_CONTINUE_RVA = 0x9880AC
POSITIVE_DOUBLE_STUB_LEN = 21
POSITIVE_TRIPLE_PREFIX = b"\x48\x8D\x3C\x7F"  # lea rdi, [rdi+rdi*2]
# IgniteEquipment 內的兩個消耗點：同裝備、材料道具。只在火煉函式內改成成功回傳。
IGNITE_REMOVE_EQUIP_CALL_RVA = 0x9862D6
IGNITE_SUB_ITEMS_CALL_RVA = 0x986196
IGNITE_MIN_CONSUME_CHECK_RVA = 0x98598C
# 舊版錯誤掛點（合流 call 前）— 每次套用前還原
LEGACY_POSITIVE_HOOK_RVA = 0x988070
LEGACY_POSITIVE_HOOK_LEN = 7

PATCHES: dict[str, tuple[int, bytes, str]] = {
    "GetRandomFlameCount": (
        0x973610,
        bytes([0xB8, 0x04, 0x00, 0x00, 0x00, 0xC3]),
        "火煉必出 4 條未燃火",
    ),
    "RandomFlameId_forceChangming_pick": (
        0x9D42F2,
        bytes([0x6A, 0x02, 0x41, 0x5E, 0x90]),
        "RandomFlameId 選火種時強制 flameId=2（長明）",
    ),
    "RandomFlameId_forceChangming_add": (
        0x9D4411,
        bytes([0x6A, 0x02, 0x41, 0x5E, 0x90]),
        "RandomFlameId 寫入列表時強制 flameId=2（長明）",
    ),
    "CheckIgniteEnough": (
        0xE124E0,
        bytes([0xB0, 0x01, 0xC3]),
        "略過火煉材料 UI 檢查",
    ),
    "Ignite_noConsume_equipment": (
        IGNITE_REMOVE_EQUIP_CALL_RVA,
        bytes([0xB0, 0x01, 0x90, 0x90, 0x90]),
        "火煉不消耗作為材料的同裝備",
    ),
    "Ignite_noConsume_items": (
        IGNITE_SUB_ITEMS_CALL_RVA,
        bytes([0xB8, 0x01, 0x00, 0x00, 0x00]),
        "火煉不消耗材料道具",
    ),
    "Ignite_allowEmptyConsume": (
        IGNITE_MIN_CONSUME_CHECK_RVA,
        b"\x90" * 6,
        "火煉允許不放同裝備與材料",
    ),
}

RESTORE_FROM_BACKUP: dict[str, tuple[int, int]] = {
    "RemoveItem": (0x9F3C80, 16),
    "Legacy_positiveDouble_hook": (LEGACY_POSITIVE_HOOK_RVA, LEGACY_POSITIVE_HOOK_LEN),
}


def build_positive_double_stub(cave_rva: int) -> bytes:
    """rdi *= 3 → mov [rbx+18],rdi → mov rdi,[rsp+0x80] → 跳回 0x9880AC。"""
    stub = bytearray()
    stub += POSITIVE_TRIPLE_PREFIX
    stub += b"\x48\x89\x7B\x18"  # mov [rbx+18], rdi
    stub += b"\x48\x8B\xBC\x24\x80\x00\x00\x00"  # mov rdi, [rsp+0x80]
    jmp_at = cave_rva + len(stub)
    jmp_rel = POSITIVE_DOUBLE_CONTINUE_RVA - (jmp_at + 5)
    stub += b"\xE9" + struct.pack("<i", jmp_rel)
    if len(stub) != POSITIVE_DOUBLE_STUB_LEN:
        raise SystemExit(f"正面 x3 stub 長度異常: {len(stub)}")
    return bytes(stub)


def _stub_looks_valid(stub: bytes, cave_rva: int) -> bool:
    if len(stub) < POSITIVE_DOUBLE_STUB_LEN or stub[:4] != POSITIVE_TRIPLE_PREFIX:
        return False
    if stub[4:8] != b"\x48\x89\x7B\x18":
        return False
    jmp_rel = struct.unpack("<i", stub[17:21])[0]
    jmp_dst = cave_rva + 17 + 5 + jmp_rel
    return jmp_dst == POSITIVE_DOUBLE_CONTINUE_RVA


def apply_positive_double(
    pe: pefile.PE, data: bytearray, backup_bytes: bytes
) -> None:
    hook_off = pe.get_offset_from_rva(POSITIVE_DOUBLE_HOOK_RVA)
    if data[hook_off] == 0xE9:
        cave_guess = POSITIVE_DOUBLE_HOOK_RVA + 5 + struct.unpack(
            "<i", data[hook_off + 1 : hook_off + 5]
        )[0]
        co = pe.get_offset_from_rva(cave_guess)
        stub = bytes(data[co : co + POSITIVE_DOUBLE_STUB_LEN])
        if _stub_looks_valid(stub, cave_guess):
            print("  [skip] IgniteFlame_positiveTriple（cave 已存在）")
            return
        print("  [fix]  IgniteFlame_positiveTriple（舊 cave 無效，重新套用）")

    stub = build_positive_double_stub(0)
    cave_rva = place_text_code(pe, data, stub)
    stub = build_positive_double_stub(cave_rva)
    cave_off = pe.get_offset_from_rva(cave_rva)
    data[cave_off : cave_off + len(stub)] = stub

    jmp = make_jmp_rel32(POSITIVE_DOUBLE_HOOK_RVA, cave_rva)
    hook_patch = jmp + b"\x90" * (POSITIVE_DOUBLE_HOOK_LEN - len(jmp))
    orig = patch_bytes(data, pe, POSITIVE_DOUBLE_HOOK_RVA, hook_patch)
    print(f"  [ok]   IgniteFlame_positiveTriple @ 0x{POSITIVE_DOUBLE_HOOK_RVA:X}")
    print(f"         cave 0x{cave_rva:X}, {orig.hex()} -> {hook_patch.hex()}")


IGNITE_NO_CONSUME_PATCHES: dict[str, tuple[int, bytes, str]] = {
    "CheckIgniteEnough": PATCHES["CheckIgniteEnough"],
    "Ignite_noConsume_equipment": PATCHES["Ignite_noConsume_equipment"],
    "Ignite_noConsume_items": PATCHES["Ignite_noConsume_items"],
    "Ignite_allowEmptyConsume": PATCHES["Ignite_allowEmptyConsume"],
}

IGNITE_CHANGMING_TRIPLE_PATCHES: dict[str, tuple[int, bytes, str]] = {
    "GetRandomFlameCount": PATCHES["GetRandomFlameCount"],
    "RandomFlameId_forceChangming_pick": PATCHES["RandomFlameId_forceChangming_pick"],
    "RandomFlameId_forceChangming_add": PATCHES["RandomFlameId_forceChangming_add"],
}


def _restore_legacy(pe: pefile.PE, data: bytearray, backup_bytes: bytes) -> None:
    for name, (rva, length) in RESTORE_FROM_BACKUP.items():
        off = pe.get_offset_from_rva(rva)
        data[off : off + length] = backup_bytes[off : off + length]
        print(f"  [restore] {name} @ RVA 0x{rva:X}")


def _apply_named_patches(
    pe: pefile.PE,
    data: bytearray,
    patches: dict[str, tuple[int, bytes, str]],
) -> None:
    for name, (rva, patch, desc) in patches.items():
        off = pe.get_offset_from_rva(rva)
        if bytes(data[off : off + len(patch)]) == patch:
            print(f"  [skip]   {name}")
            continue
        patch_bytes(data, pe, rva, patch)
        print(f"  [ok]     {name} @ 0x{rva:X} — {desc}")


def apply_ignite_no_consume(pe: pefile.PE, data: bytearray, backup_bytes: bytes) -> None:
    _restore_legacy(pe, data, backup_bytes)
    _apply_named_patches(pe, data, IGNITE_NO_CONSUME_PATCHES)


def apply_ignite_changming_triple(pe: pefile.PE, data: bytearray, backup_bytes: bytes) -> None:
    _restore_legacy(pe, data, backup_bytes)
    _apply_named_patches(pe, data, IGNITE_CHANGMING_TRIPLE_PATCHES)
    apply_positive_double(pe, data, backup_bytes)


def apply_all_ignite_patches(pe: pefile.PE, data: bytearray, backup_bytes: bytes) -> None:
    _restore_legacy(pe, data, backup_bytes)
    _apply_named_patches(pe, data, IGNITE_NO_CONSUME_PATCHES)
    _apply_named_patches(pe, data, IGNITE_CHANGMING_TRIPLE_PATCHES)
    apply_positive_double(pe, data, backup_bytes)


def apply_patches(restore: bool = False) -> None:
    if not DLL.exists():
        raise SystemExit(f"找不到 {DLL}")

    if restore:
        if not BACKUP.exists():
            raise SystemExit(f"沒有備份檔 {BACKUP}")
        shutil.copy2(BACKUP, DLL)
        print(f"已還原: {DLL}")
        return

    if not BACKUP.exists():
        shutil.copy2(DLL, BACKUP)
        print(f"已備份: {BACKUP}")

    pe = pefile.PE(str(BACKUP))
    data = bytearray(BACKUP.read_bytes())
    backup_bytes = bytes(BACKUP.read_bytes())

    print(f"修補前 SHA256（備份）: {sha256(BACKUP)}")
    apply_all_ignite_patches(pe, data, backup_bytes)
    write_dll(data, BACKUP)
    print("完成。請重啟遊戲後測試火煉（4 條長明，正面數值 x3）。")


if __name__ == "__main__":
    restore = "--restore" in sys.argv
    apply_patches(restore=restore)
