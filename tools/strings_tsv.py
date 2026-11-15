"""strings_tsv.py: build/strings.tsv for text coverage ($SKILL/scripts/textcover.py): one "id<TAB>hex address" per
script/ entry, the CPU address (0x08xxxxxx) the game reads the text's first byte from in a built ROM.

    python -X utf8 tools/strings_tsv.py [ROM] [--out build/strings.tsv]

Messages (sSSS.KK): the script file the ROM's resource directory points at (it moves when it grows), script SSS's
KK-th message op, text at op + 6 (the warp's TEXT_DRAW hook logs that address). Strings (tOOOOOO): the address the
first pointer word holds (moved strings follow it), else the original slot. Debug-only and kept entries are
listed too: textcover's waiver file says which never show.
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import insert  # noqa: E402
import script  # noqa: E402

BUS = 0x08000000
OUT = ROOT / "build" / "strings.tsv"


def rows(rom, entries):
    base = struct.unpack_from("<I", rom, script.DIR_WORD)[0] - BUS
    offs = script.offsets(rom, base)
    out = []
    for i, ops in enumerate(script.unpack(rom, base)):
        k = 0
        for op in ops:
            if op.code == script.MSG:
                out.append((f"s{i:03d}.{k:02d}", BUS + base + offs[i] + op.off + 6))
                k += 1
    for e in entries.values():
        if e["id"].startswith("t"):
            ptrs = e.get("ptrs") or []
            addr = struct.unpack_from("<I", rom, int(ptrs[0], 16))[0] if ptrs else BUS + int(e["id"][1:], 16)
            out.append((e["id"], addr))
    return out


def write(rom, path=OUT):
    r = rows(rom, insert.load_entries())
    path.write_text("".join(f"{i}\t{a:08X}\n" for i, a in r), encoding="utf-8", newline="\n")
    return len(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "dynadevice_blue_en.gba"))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    n = write(Path(a.rom).read_bytes(), Path(a.out))
    print(f"{a.out}: {n} ids")


if __name__ == "__main__":
    main()
