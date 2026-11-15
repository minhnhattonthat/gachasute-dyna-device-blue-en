"""rawimg_sheet.py: contact sheets of every raw (uncompressed) "IMG\\0" block the graphics archive reaches.

    python -X utf8 tools/rawimg_sheet.py [--out work/gfx/raw] [--zoom 2]

blockscan.py / blockfind.py / gfx_sweep.py only see ECD-compressed blocks; raw IMG blocks (e.g. 01E5464, the
field HUD) are stored as is. Each tile of the sheets is one block, labelled with its offset, drawn in its raw PLT
when one follows it, else in grey ramps. Look for Japanese, then redraw with gfx/<OFFSET>.png like any block.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

GREY = [(i * 17, i * 17, i * 17) for i in range(16)]


def raw_blocks(rom):
    return sorted(o for o in gfx.archive_words(rom) if gfx.is_raw(rom, o) and rom[o + 4] == 0)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(gfx.ROOT / "work" / "gfx" / "raw"))
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--per", type=int, default=48, help="blocks per sheet")
    a = ap.parse_args(argv)
    rom = gfx.ROM.read_bytes()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    offs = raw_blocks(rom)
    cells = []
    for o in offs:
        try:
            pal = gfx.palette_for(rom, o)[0]
        except ValueError:
            pal = GREY
        img = gfx.to_png(gfx.load(rom, o), pal)
        cells.append((o, img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)))
    for s in range(0, len(cells), a.per):
        chunk = cells[s:s + a.per]
        cw = max(c.width for _, c in chunk) + 8
        ch = max(c.height for _, c in chunk) + 14
        cols = 6
        sheet = Image.new("RGB", (cols * cw, ((len(chunk) + cols - 1) // cols) * ch), (60, 0, 60))
        d = ImageDraw.Draw(sheet)
        for i, (o, c) in enumerate(chunk):
            x, y = (i % cols) * cw, (i // cols) * ch
            d.text((x + 2, y), f"{o:07X}", fill=(255, 255, 0))
            sheet.paste(c, (x + 2, y + 12))
        p = out / f"raw_{s // a.per:02d}.png"
        sheet.save(p)
        print(p, len(chunk))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
