"""strtab.py: the NUL-terminated string region 0x0AF6D0-0x0BB7C0 (menus, item / Dyna / part names, help text,
name-entry keyboard, the leftover AGB debug menu) and the pointers that reach each string.

    python -X utf8 tools/strtab.py            # summary: strings, pointers, sources by area

Layout (docs/re/text.md): strings start 4-aligned, end in NUL, zero-padded to the next start. Every string has at
least one direct u32 pointer (0x08000000 | offset) in a code literal pool (0x008980-0x0A3254) or in the data
tables after the region (0x0BDAE8-0x0E4674). Words that match a string start elsewhere (graphics, the address
database) are coincidences and are not pointers; only the two areas below are searched, 4-aligned (the CPU's
ldr needs it, and no 2-aligned source exists there).
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
LO, HI = 0x0AF6D0, 0x0BB7C0       # region; "FLASH_V126" (save-type signature, never touch) follows at 0x0BB7C4
DEBUG = (0x0AF6E0, 0x0AFCA0)      # "--- AGB SYSTEM  DEBUG MENU ---" and its romaji items
SOURCES = [(0x000000, LO), (HI, 0x0E7FA4)]  # code; data tables up to the graphics resource file


def pieces(rom):
    """-> list of (start, raw bytes without NUL, slot bytes up to the next string or the region end)."""
    out = []
    a = LO
    while a < HI:
        if rom[a] == 0:
            a += 1
            continue
        e = rom.index(b"\0", a)
        out.append([a, rom[a:e]])
        a = e + 1
    for k, p in enumerate(out):
        nxt = out[k + 1][0] if k + 1 < len(out) else HI
        p.append(nxt - p[0])
    return [tuple(p) for p in out]


def pointers(rom, starts):
    """-> {string start: [ROM offsets of u32 words holding 0x08000000 + start]} over SOURCES, 4-aligned."""
    want = {0x08000000 + s for s in starts}
    found = {s: [] for s in starts}
    for lo, hi in SOURCES:
        for a in range(lo, hi - 3, 4):
            w = struct.unpack_from("<I", rom, a)[0]
            if w in want:
                found[w - 0x08000000].append(a)
    return found


def main():
    rom = ROM.read_bytes()
    ps = pieces(rom)
    ptr = pointers(rom, [p[0] for p in ps])
    total = sum(map(len, ptr.values()))
    none = [hex(s) for s, v in ptr.items() if not v]
    print(f"{len(ps)} strings, {total} pointers, {len(none)} without a pointer {none[:10]}")
    return 1 if none else 0


if __name__ == "__main__":
    sys.exit(main())
