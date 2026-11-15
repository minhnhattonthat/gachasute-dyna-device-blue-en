"""pxdump.py: print the palette indices of a region of an ECD block (original ROM, or a build), one hex digit a pixel.

    python -X utf8 tools/pxdump.py OFFSET X0 Y0 X1 Y1 [--rom build/dynadevice_blue_en.gba]
    e.g. tools/pxdump.py 022CF64 32 0 96 16

OFFSET: the block's ECD offset (docs/re/graphics.md). X/Y: atlas pixels, end exclusive. '.' = index 0.
Use it to read an atlas's ink, outline and shading indices before writing a gfx_text.py entry.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("off")
    ap.add_argument("box", nargs=4, type=int)
    ap.add_argument("--rom", default=str(ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    off = int(a.off, 16)
    w, h, px = gfx.indices(ecd.decompress(rom, off)[0])
    x0, y0, x1, y1 = a.box
    print(f"{a.off}: {w}x{h}; x {x0}..{x1 - 1}")
    for y in range(y0, min(y1, h)):
        print(f"{y:3d} " + "".join("." if px[y * w + x] == 0 else "%x" % px[y * w + x] for x in range(x0, min(x1, w))))


if __name__ == "__main__":
    main()
