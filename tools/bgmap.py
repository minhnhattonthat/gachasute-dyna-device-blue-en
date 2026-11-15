"""bgmap.py: which screen cells of each text BG show tiles of one graphics block (from a ppu dump).

    python -X utf8 tools/bgmap.py DUMP_PREFIX VRAM_HEX [--cols 32] [--count N] [--full]
    e.g. tools/bgmap.py work/qa/form_dump/form/ppu_001200 9000

DUMP_PREFIX: ppu_every.lua / ppudump output without the extension (.vram.bin and .io.bin are read).
VRAM_HEX: VRAM byte address of the block's tile 0 (vramfind.py: VRAM addr - (block offset - 8)).
Prints, for every BG whose map uses the block, the visible 30x20 cells (after hofs/vofs) as atlas `row,col`
(tile number / --cols, the block's PNG width in tiles), '.' for other tiles. Text BGs (mode 0/1) only.
"""
import struct
import sys
from pathlib import Path


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    prefix, base = argv[0], int(argv[1], 16)
    cols = int(argv[argv.index("--cols") + 1]) if "--cols" in argv else 32
    count = int(argv[argv.index("--count") + 1]) if "--count" in argv else 1024
    full = "--full" in argv   # whole map from (0,0): the io dump's scroll registers can be stale
    vram = Path(prefix + ".vram.bin").read_bytes()
    io = Path(prefix + ".io.bin").read_bytes()
    dispcnt = struct.unpack_from("<H", io, 0)[0]
    for bg in range(4):
        if not dispcnt & (0x100 << bg):
            continue
        cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
        hofs = struct.unpack_from("<H", io, 0x10 + 4 * bg)[0] & 0x1FF
        vofs = struct.unpack_from("<H", io, 0x12 + 4 * bg)[0] & 0x1FF
        cbase = ((cnt >> 2) & 3) * 0x4000
        sbase = ((cnt >> 8) & 0x1F) * 0x800
        size = cnt >> 14
        mw = 64 if size in (1, 3) else 32
        mh = 64 if size in (2, 3) else 32
        if cnt & 0x80:
            continue   # 8bpp: not handled

        def entry(x, y):
            blk = (x // 32) + (y // 32) * (mw // 32) if mw == 64 else (y // 32)
            off = sbase + blk * 0x800 + ((y % 32) * 32 + (x % 32)) * 2
            return struct.unpack_from("<H", vram, off)[0]

        if full:
            hofs = vofs = 0
        grid, hit = [], False
        for sy in range(mh if full else 20):
            line = []
            for sx in range(mw if full else 30):
                x = (sx + hofs // 8) % mw
                y = (sy + vofs // 8) % mh
                e = entry(x, y)
                t = e & 0x3FF
                addr = cbase + 32 * t
                n = (addr - base) // 32
                if addr >= base and n < count and addr < 0x10000:
                    hit = True
                    fl = ("h" if e & 0x400 else "") + ("v" if e & 0x800 else "")
                    line.append(f"{n // cols},{n % cols}{fl}".rjust(6))
                else:
                    line.append("     .")
            grid.append("".join(line))
        if hit:
            print(f"BG{bg} cnt={cnt:04X} char=0x{cbase:05X} screen=0x{sbase:05X} hofs={hofs} vofs={vofs} "
                  f"pal-bits per cell not shown")
            for sy, line in enumerate(grid):
                print(f"{sy:2d} {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
