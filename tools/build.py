"""build.py: build build/dynadevice_blue_en.gba from the dump listed in rom.sha1.

    python -X utf8 tools/build.py [--out build/dynadevice_blue_en.gba]

Phase 3 (identity): unpacks the event-script file into ops and packs it again, so with no edits the output is
byte-identical to the original (tests/test_build.py). Later phases feed translated scripts in through build().
Prints the output's SHA-1 and whether it equals the original.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import script  # noqa: E402

ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
OUT = ROOT / "build" / "dynadevice_blue_en.gba"
# Zero-filled free space at the end of the 8 MiB ROM (0x747D94..0x800000, docs/re/text.md); 16-aligned start.
FREE_START, FREE_END = 0x747DA0, 0x800000


def place_script_file(out, blob):
    """Write the packed script file in its original slot if it fits, else at FREE_START, and point the resource
    directory at it. Returns the ROM offset used."""
    if len(blob) <= script.END - script.BASE:
        at = script.BASE
        out[at:script.END] = blob + bytes(script.END - script.BASE - len(blob))
    else:
        at = FREE_START
        if at + len(blob) > FREE_END:
            raise ValueError(f"script file of {len(blob)} bytes does not fit in the free space")
        out[at:at + len(blob)] = blob
    out[script.DIR_WORD:script.DIR_WORD + 4] = (0x08000000 + at).to_bytes(4, "little")
    return at


def build(rom, scripts=None):
    """-> the built ROM image (bytearray). scripts: 834 op lists (script.unpack); None = the original ones."""
    out = bytearray(rom)
    if scripts is None:
        scripts = script.unpack(rom)
    place_script_file(out, script.pack(scripts))
    return out


def stress_scripts(rom):
    """Every message gets "＊" (SJIS 81 96) appended, so the file outgrows its slot: an in-game check of the jump
    fix-ups and the relocation (build.py --stress, then warp scenes on it)."""
    scripts = script.unpack(rom)
    for ops in scripts:
        for op in ops:
            if op.code == script.MSG and len(op.text) % 2 == 0:
                op.text += "＊".encode("cp932")
    return scripts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--stress", action="store_true", help="append ＊ to every message (relocation test build)")
    a = ap.parse_args()
    check_rom.check()
    rom = ROM.read_bytes()
    out = build(rom, stress_scripts(rom) if a.stress else None)
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)
    sha = hashlib.sha1(out).hexdigest()
    print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {len(out)} bytes, sha1 {sha}"
          f"{' (identical to the original)' if out == rom else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
