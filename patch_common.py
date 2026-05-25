"""Shared helpers for GameAssembly.dll binary patches."""
from __future__ import annotations

import hashlib
import shutil
import struct
from pathlib import Path

import pefile

GAME_ROOT = Path(__file__).resolve().parent.parent
DLL = GAME_ROOT / "GameAssembly.dll"
IMAGE_BASE = 0x180000000

# .text 尾端零填充上界（再往上是 0x4EEA00 起的真實程式，不可覆寫）
TEXT_CAVE_SCAN_END_RVA = 0x4EEA00


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rva_to_offset(pe: pefile.PE, rva: int) -> int:
    return pe.get_offset_from_rva(rva)


def patch_bytes(data: bytearray, pe: pefile.PE, rva: int, patch: bytes) -> bytes:
    off = rva_to_offset(pe, rva)
    original = bytes(data[off : off + len(patch)])
    data[off : off + len(patch)] = patch
    return original


def make_jmp_rel32(src_rva: int, dst_rva: int) -> bytes:
    rel = dst_rva - (src_rva + 5)
    return b"\xE9" + struct.pack("<i", rel)


def get_section(pe: pefile.PE, name: str) -> pefile.SectionStructure:
    target = name.encode() if isinstance(name, str) else name
    for s in pe.sections:
        if s.Name.rstrip(b"\x00") == target:
            return s
    raise SystemExit(f"找不到 section {name!r}")


def get_text_section(pe: pefile.PE) -> pefile.SectionStructure:
    return get_section(pe, ".text")


def next_section_rva(pe: pefile.PE, section: pefile.SectionStructure) -> int:
    """RVA of the section that follows `section` in memory layout."""
    end = section.VirtualAddress + section.Misc_VirtualSize
    best = pe.OPTIONAL_HEADER.SizeOfImage
    for s in pe.sections:
        if s.VirtualAddress >= end and s.VirtualAddress < best:
            best = s.VirtualAddress
    return best


def _align_up(value: int, align: int) -> int:
    return (value + align - 1) // align * align


def _is_zero_padding(buf: bytes) -> bool:
    return all(b in (0x00, 0xCC) for b in buf)


def find_zero_cave_rva(
    pe: pefile.PE,
    data: bytearray,
    blob_len: int,
    *,
    section: pefile.SectionStructure | None = None,
    start_rva: int | None = None,
    scan_end_rva: int | None = None,
) -> int | None:
    """在區段內找一段零填充可寫入 blob_len 位元組的 RVA。"""
    section = section or get_text_section(pe)
    limit = next_section_rva(pe, section)
    raw_end = section.VirtualAddress + section.SizeOfRawData
    end = min(limit, raw_end, scan_end_rva or limit)
    start = section.VirtualAddress if start_rva is None else start_rva
    rva = _align_up(start, 16)
    while rva + blob_len <= end:
        off = rva_to_offset(pe, rva)
        if off + blob_len > len(data):
            break
        if _is_zero_padding(bytes(data[off : off + blob_len])):
            return rva
        rva += 16
    return None


def sync_pe_headers(pe: pefile.PE, data: bytearray) -> None:
    """Write updated section / optional headers into the PE bytearray."""
    for section in pe.sections:
        hdr = section.get_file_offset()
        struct.pack_into("<I", data, hdr + 8, section.Misc_VirtualSize)
        struct.pack_into("<I", data, hdr + 16, section.SizeOfRawData)
        struct.pack_into("<I", data, hdr + 20, section.PointerToRawData)
    oh = pe.OPTIONAL_HEADER.get_file_offset()
    struct.pack_into("<I", data, oh + 56, pe.OPTIONAL_HEADER.SizeOfImage)


def _refresh_size_of_image(pe: pefile.PE) -> None:
    sect_align = pe.OPTIONAL_HEADER.SectionAlignment
    last = max(s.VirtualAddress + s.Misc_VirtualSize for s in pe.sections)
    pe.OPTIONAL_HEADER.SizeOfImage = _align_up(last, sect_align)


def place_text_code(pe: pefile.PE, data: bytearray, blob: bytes) -> int:
    """
    在 .text 既有 raw 零填充區寫入 code cave。
    不擴大 Misc_VirtualSize，避免 .text 虛擬範圍頂到 il2cpp (0x4EF000)。
    """
    text = get_text_section(pe)
    scan_start = max(text.VirtualAddress, 0x4EE850)
    cave_rva = find_zero_cave_rva(
        pe,
        data,
        len(blob),
        section=text,
        start_rva=scan_start,
        scan_end_rva=TEXT_CAVE_SCAN_END_RVA,
    )
    if cave_rva is None:
        raise SystemExit(
            f".text 零填充區不足 (需要 {len(blob)} 位元組，"
            f"可用至 RVA 0x{TEXT_CAVE_SCAN_END_RVA:X})。"
        )
    off = rva_to_offset(pe, cave_rva)
    if off + len(blob) > len(data):
        raise SystemExit("code cave 超出檔案大小")
    data[off : off + len(blob)] = blob
    return cave_rva


def append_to_section_file(
    pe: pefile.PE, data: bytearray, section: pefile.SectionStructure, blob: bytes
) -> int:
    """在區段檔案尾端插入資料，並更新後續區段的 PointerToRawData。"""
    file_align = pe.OPTIONAL_HEADER.FileAlignment
    sect_align = pe.OPTIONAL_HEADER.SectionAlignment
    limit = next_section_rva(pe, section)

    raw_end_rva = section.VirtualAddress + section.SizeOfRawData
    cave_rva = _align_up(raw_end_rva, 16)
    if cave_rva + len(blob) > limit:
        sec = section.Name.rstrip(b"\x00").decode("ascii", "replace")
        raise SystemExit(
            f"{sec} 空間不足 (需要至 0x{cave_rva + len(blob):X}, 下一區段 0x{limit:X})"
        )

    insert_at = section.PointerToRawData + section.SizeOfRawData
    pad = cave_rva - raw_end_rva
    chunk = b"\x00" * pad + blob
    chunk = chunk.ljust(_align_up(len(chunk), file_align), b"\x00")

    data[insert_at:insert_at] = chunk

    for s in pe.sections:
        if s.PointerToRawData >= insert_at:
            s.PointerToRawData += len(chunk)

    section.SizeOfRawData += len(chunk)
    need_vsz = cave_rva + len(blob) - section.VirtualAddress
    if section.VirtualAddress + need_vsz > limit:
        sec = section.Name.rstrip(b"\x00").decode("ascii", "replace")
        raise SystemExit(
            f"擴充後 {sec} 虛擬大小會碰到下一區段 (0x{limit:X})"
        )
    if need_vsz > section.Misc_VirtualSize:
        # 勿對齊到 SectionAlignment，否則易與下一區段虛擬位址重疊
        section.Misc_VirtualSize = need_vsz

    _refresh_size_of_image(pe)
    sync_pe_headers(pe, data)
    return cave_rva


def append_to_rdata(pe: pefile.PE, data: bytearray, blob: bytes) -> int:
    """將唯讀資料附加到 .rdata 檔案尾端（插入檔案，不覆寫 .data）。"""
    return append_to_section_file(pe, data, get_section(pe, ".rdata"), blob)


def append_to_text(pe: pefile.PE, data: bytearray, blob: bytes) -> int:
    """Place a code cave in .text zero padding (alias for place_text_code)."""
    return place_text_code(pe, data, blob)


def write_dll(data: bytearray, backup: Path) -> None:
    if not backup.exists():
        shutil.copy2(DLL, backup)
        print(f"已備份: {backup}")
    else:
        print(f"備份已存在: {backup}")

    print(f"修補前 SHA256: {sha256(DLL)}")
    patched = DLL.with_suffix(".dll.patched")
    patched.write_bytes(data)
    try:
        shutil.copy2(patched, DLL)
        patched.unlink(missing_ok=True)
    except OSError as e:
        print(f"無法直接寫入 {DLL.name}（請關閉遊戲）: {e}")
        print(f"已寫入: {patched}")
        raise SystemExit(1) from e
    print(f"修補後 SHA256: {sha256(DLL)}")
