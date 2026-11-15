"""blockscan.py: which graphics-text blocks (docs/re/graphics.md "Rows") each scene's ppu dumps show.

    python -X utf8 tools/blockscan.py DIR.. [--min 6] [--all]
    e.g. tools/blockscan.py work/qa/survey/*      (dirs of a `regen.py .. --probe tools/lua/ppu_every.lua` run)

For every DIR, every ppu_*.vram.bin in it is matched against the IMG blocks of the original ROM (as in
tools/blockfind.py: tiles that are not one flat colour, 32-byte aligned in VRAM), using only the tiles no other
block holds. A block counts as shown when at least --min of those tiles are in VRAM in one dump. Run it on dumps of
the ORIGINAL ROM: an English build's redrawn blocks no longer match. Prints, per block of the graphics.md Rows table (or every
block with --all), the scenes that show it, the frame with the most tiles, and whether gfx/<OFFSET>.png exists.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def block_tiles(rom):
    out = {}
    for off, *_, kind in ((b[0], b[3]) for b in gfx.blocks(rom)):
        if kind != "IMG":
            continue
        try:
            body = ecd.decompress(rom, off)[0][8:]
        except Exception:   # noqa: BLE001 - odd blocks: skip
            continue
        tiles = {body[i:i + 32] for i in range(0, len(body) - 31, 32)}
        out[off] = {t for t in tiles if t.count(t[0]) != 32}
    owners = {}
    for tiles in out.values():
        for t in tiles:
            owners[t] = owners.get(t, 0) + 1
    # tiles shared with another block (box corners, blank-ish runs) prove nothing: keep each block's own tiles
    return {off: {t for t in tiles if owners[t] == 1} for off, tiles in out.items()}


def table_rows():
    text = (ROOT / "docs/re/graphics.md").read_text(encoding="utf-8")
    return {int(m.group(1), 16): m.group(2).strip()
            for m in re.finditer(r"^\| ([0-9A-F]{7}) \| sheet_\d+ \| ([^|]*)\|", text, re.M)}


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    least = int(argv[argv.index("--min") + 1]) if "--min" in argv else 6
    every = "--all" in argv
    dirs = [Path(a) for a in argv if not a.startswith("-") and Path(a).is_dir()]
    blocks = block_tiles(gfx.ROM.read_bytes())
    rows = table_rows()
    want = blocks if every else {o: blocks[o] for o in rows if o in blocks}
    hits = {}   # off -> {scene: (count, frame)}
    for d in dirs:
        for dump in sorted(d.glob("ppu_*.vram.bin")):
            vram = dump.read_bytes()
            have = {vram[i:i + 32] for i in range(0, len(vram) - 31, 32)}
            for off, tiles in want.items():
                n = len(tiles & have)
                if n >= least:
                    best = hits.setdefault(off, {}).get(d.name, (0, ""))
                    if n > best[0]:
                        hits[off][d.name] = (n, dump.name.split(".")[0])
    for off in sorted(want):
        done = "done" if (ROOT / f"gfx/{off:07X}.png").exists() else "JP  "
        seen = hits.get(off, {})
        where = ", ".join(f"{s} {n}/{len(want[off])} {f}" for s, (n, f) in sorted(seen.items())) or "-"
        if seen or not every:
            print(f"{off:07X} {done} {rows.get(off, '')[:28]:28}  {where}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
