"""blockfind.py: which ECD IMG blocks a ppu dump shows (counts of each block's distinct tiles found in VRAM).

    python -X utf8 tools/blockfind.py DUMP_PREFIX [--top 10] [--min 4]
    e.g. tools/blockfind.py work/qa/warp/d_get/ppu_000600

DUMP_PREFIX: ppu_every.lua / ppudump output without the extension (.vram.bin is read). For each IMG block of the
original ROM (archive 0, docs/re/compression.md) it counts the tiles that are not one flat colour and appear
32-byte aligned in VRAM, and prints the best blocks with the VRAM address of their tile 0 when the tiles sit in
block order (2D OBJ blocks: tile (r, c) at base + 32 * (32 * r + c); BG: base + 32 * n). Then look the offset
up in docs/re/graphics.md "Rows" and export it with tools/gfx.py export OFFSET.
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 10
    least = int(argv[argv.index("--min") + 1]) if "--min" in argv else 4
    vram = Path(argv[0] + ".vram.bin").read_bytes()
    pos = {}
    for i in range(0, len(vram) - 31, 32):
        pos.setdefault(vram[i:i + 32], []).append(i)
    rom = gfx.ROM.read_bytes()
    rows = []
    for off, *_, kind in ((b[0], b[3]) for b in gfx.blocks(rom)):
        if kind != "IMG":
            continue
        try:
            raw = ecd.decompress(rom, off)[0]
            w, _, _ = gfx.indices(raw)
        except Exception:   # noqa: BLE001 - odd blocks: skip
            continue
        body = raw[8:]
        cols = max(w // 8, 1)
        seen, bases = set(), Counter()
        for t in range(len(body) // 32):
            tb = body[32 * t:32 * t + 32]
            if tb.count(tb[0]) == 32 or tb in seen:
                continue
            seen.add(tb)
            r, c = divmod(t, cols)
            for v in pos.get(tb, ()):
                bases[v - 32 * t] += 1
                bases[("2d", v - 32 * (32 * r + c))] += 1
        found = sum(1 for tb in seen if tb in pos)
        if found >= least:
            base, n = bases.most_common(1)[0] if bases else (None, 0)
            where = (f"2D base 0x{base[1]:05X}" if isinstance(base, tuple) else f"base 0x{base:05X}") if base is not None else "-"
            rows.append((found, len(seen), off, where, n))
    for found, total, off, where, n in sorted(rows, reverse=True)[:top]:
        print(f"{off:07X}  {found:4d}/{total:<4d} tiles in VRAM  {where} ({n} in order)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
