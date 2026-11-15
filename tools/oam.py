"""oam.py: list the visible sprites of a ppu dump (ppu_every.lua / ppudump output).

    python -X utf8 tools/oam.py work/qa/warp/SCENE            # last ppu_*.oam.bin in that directory
    python -X utf8 tools/oam.py work/qa/warp/SCENE/ppu_000930  # one dump

Prints index, x, y, size, tile (and its row/col in a 32-tile-wide 2D OBJ layout), palette, priority. Sprites parked
off screen (y 160, or the 8x8 tile-0 fillers at y -16) are skipped. DISPCNT bit 6 clear = 2D mapping: OBJ tile
r*32+c then equals block tile (r, c) when a 256 px wide block is loaded at OBJ tile 0 (PDA, title, link screens).
"""
import glob
import struct
import sys
from pathlib import Path

SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def main(arg):
    p = Path(arg)
    f = Path(str(p) + ".oam.bin") if not p.is_dir() else Path(sorted(glob.glob(str(p / "ppu_*.oam.bin")))[-1])
    io = f.with_name(f.name.replace(".oam.bin", ".io.bin"))
    print(f, f"DISPCNT {struct.unpack_from('<H', io.read_bytes(), 0)[0]:04x}" if io.exists() else "")
    d = f.read_bytes()
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<3H", d, i * 8)
        if (a0 >> 8) & 3 == 2:   # disabled
            continue
        y, x = a0 & 0xFF, a1 & 0x1FF
        x -= 512 if x >= 256 else 0
        y -= 256 if y >= 160 else 0
        w, h = SIZES[a0 >> 14][a1 >> 14]
        tile = a2 & 0x3FF
        if y == 160 - 256 or (tile == 0 and y == -16 and w == 8 and h == 8):
            continue
        print(f"{i:3d} x{x:4d} y{y:4d} {w}x{h} tile {tile} (r{tile // 32} c{tile % 32}) pal {a2 >> 12} prio {(a2 >> 10) & 3}")


if __name__ == "__main__":
    main(sys.argv[1])
