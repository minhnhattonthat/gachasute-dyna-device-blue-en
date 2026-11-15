"""pat.py: list the sprite frames of the game's "PAT\\0" animation blocks (raw, uncompressed, in ROM).

    python -X utf8 tools/pat.py OFF [OFF..]          # one PAT block (ROM offset of its "PAT\\0" magic)
    python -X utf8 tools/pat.py --scan LO HI         # every PAT block in a ROM range, frames included

Layout (docs/re/graphics.md): "PAT\\0", u32 frame count, u32 offsets from the magic; a frame = s16 count + 8-byte
entries (u16 size code | 0x2000 (shape bits 6-7, size bits 4-5), s16 x, s16 y, u16 tile | pal << 12), x/y relative to the object's anchor. Tile
row/col assume a 32-tile-wide 2D OBJ layout. Prints each entry's ROM offset, so a patch (gfx.MAP_PATCHES style)
can point at the word to change: tile word = entry + 6, x = entry + 2.
"""
import struct
import sys
from pathlib import Path

ROM = Path(__file__).resolve().parents[1] / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
SHAPES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
          2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def frames(rom, off):
    """-> [(frame offset, [(entry offset, w, h, x, y, tile, pal)])]."""
    if rom[off:off + 4] != b"PAT\0":
        raise ValueError("no PAT magic at %X" % off)
    n = struct.unpack_from("<I", rom, off + 4)[0]
    out = []
    for k in range(n):
        f = off + struct.unpack_from("<I", rom, off + 8 + 4 * k)[0]
        cnt = struct.unpack_from("<h", rom, f)[0]
        ents = []
        for e in range(cnt):
            p = f + 2 + 8 * e
            a, x, y, t = struct.unpack_from("<HhhH", rom, p)
            shape, size = (a >> 6) & 3, (a >> 4) & 3   # 0x00 8x8, 0x41 16x8, 0x52 32x8, 0x66 32x16
            w, h = SHAPES.get(shape, [(0, 0)] * 4)[size]
            ents.append((p, w, h, x, y, t & 0x3FF, t >> 12))
        out.append((f, ents))
    return out


def show(rom, off):
    print("PAT %07X" % off)
    for k, (f, ents) in enumerate(frames(rom, off)):
        print("  frame %d at %07X, %d sprites" % (k, f, len(ents)))
        for p, w, h, x, y, t, pal in ents:
            print("    %07X %2dx%-2d x %4d y %4d tile %4d (r%d c%d) pal %d" % (p, w, h, x, y, t, t // 32, t % 32, pal))


def main(argv):
    rom = ROM.read_bytes()
    if argv[:1] == ["--scan"]:
        lo, hi = int(argv[1], 16), int(argv[2], 16)
        i = rom.find(b"PAT\0", lo, hi)
        while i >= 0:
            try:
                show(rom, i)
            except (struct.error, ValueError) as e:
                print("PAT %07X: unreadable (%s)" % (i, e))
            i = rom.find(b"PAT\0", i + 4, hi)
        return 0
    if not argv:
        print(__doc__)
        return 2
    for a in argv:
        show(rom, int(a, 16))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
