"""gfx_sweep.py: render every ECD IMG block in the ROM into numbered contact sheets for the graphics-text survey.

    python -X utf8 tools/gfx_sweep.py [--out work/gfx_sweep] [--per 40]

Each IMG uses the nearest PLT block after it in ROM (the game stores them in pairs), else a grey ramp.
Writes sheet_NNN.png (cells labelled with the ROM offset) and index.tsv (offset, w, h, flag, palette offset).
Prints every IMG it skipped and why."""
import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = next((ROOT / "rom").glob("*.gba"))


def palette(raw):
    n = struct.unpack_from("<H", raw, 4)[0] or 16
    cols = []
    for i in range(min(n, 256)):
        v = struct.unpack_from("<H", raw, 8 + 2 * i)[0] if 8 + 2 * i + 2 <= len(raw) else 0
        cols.append(((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8))
    return cols


GREY = [(i * 17, i * 17, i * 17) for i in range(16)]


def render(raw, pal):
    flag, w, h = raw[4], raw[5], raw[6]
    data = raw[8:]
    bpp8 = flag != 0 and len(data) >= w * h * 64
    tile_bytes = 64 if bpp8 else 32
    if w == 0 or h == 0 or len(data) < w * h * tile_bytes:
        return None, "size mismatch flag=%d w=%d h=%d len=%d" % (flag, w, h, len(data))
    img = Image.new("RGB", (w * 8, h * 8))
    px = img.load()
    for t in range(w * h):
        tx, ty = t % w, t // w
        base = t * tile_bytes
        for y in range(8):
            for x in range(8):
                if bpp8:
                    c = data[base + y * 8 + x]
                else:
                    b = data[base + y * 4 + x // 2]
                    c = b >> 4 if x & 1 else b & 15
                px[tx * 8 + x, ty * 8 + y] = pal[c] if c < len(pal) else (255, 0, 255)
    return img, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "gfx_sweep"))
    ap.add_argument("--per", type=int, default=40)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = ROM.read_bytes()
    blocks = ecd.scan(data)
    cells, index = [], []
    for i, (off, _il, _ol, tag) in enumerate(blocks):
        if tag != "IMG":
            continue
        raw, _ = ecd.decompress(data, off)
        pal, pal_off = GREY, "-"
        for j in range(i + 1, min(i + 4, len(blocks))):
            if blocks[j][3] == "PLT":
                pal, pal_off = palette(ecd.decompress(data, blocks[j][0])[0]), "%07X" % blocks[j][0]
                break
        img, why = render(raw, pal)
        if img is None:
            print("skip %07X: %s" % (off, why))
            continue
        scale = 2 if img.width <= 128 and img.height <= 128 else 1
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
        cells.append(("%07X" % off, img))
        index.append("%07X\t%d\t%d\t%d\t%s" % (off, raw[5], raw[6], raw[4], pal_off))
    (out / "index.tsv").write_text("offset\tw_tiles\th_tiles\tflag\tpalette\n" + "\n".join(index) + "\n", encoding="utf-8")
    for s in range(0, len(cells), a.per):
        chunk = cells[s:s + a.per]
        width = 960
        x = y = rowh = 0
        placed = []
        for name, img in chunk:
            cw, ch = max(img.width, 70), img.height + 12
            if x + cw > width:
                x, y, rowh = 0, y + rowh + 6, 0
            placed.append((x, y, name, img))
            x += cw + 6
            rowh = max(rowh, ch)
        sheet = Image.new("RGB", (width, y + rowh + 6), (40, 40, 48))
        d = ImageDraw.Draw(sheet)
        for x, y, name, img in placed:
            d.text((x, y), name, fill=(255, 255, 0))
            sheet.paste(img, (x, y + 12))
        sheet.save(out / ("sheet_%03d.png" % (s // a.per)))
    print("%d images on %d sheets in %s" % (len(cells), (len(cells) + a.per - 1) // a.per, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
