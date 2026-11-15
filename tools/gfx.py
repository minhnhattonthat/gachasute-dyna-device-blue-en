"""gfx.py: graphics text - export ECD IMG blocks to PNG and put edited PNGs back into the build.

    python -X utf8 tools/gfx.py export OFF [OFF..]   # work/gfx/orig/OFF.png (1x) and OFF_x4.png, palette = next PLT
    python -X utf8 tools/gfx.py check                # every gfx/*.png converts (palette, size); prints sizes

Every ECD block lives in archive 0 of the resource table at 0x080BBDE8 (docs/re/compression.md): the archive at
ROM 0x0E7FA4 starts with u32 offsets relative to itself, and the loader (0x08003074) reads block = base + off[i].
An edited block is written in its old slot when it fits (up to the next block), else into free space with every
archive word that pointed at it rewritten. One English image per block: gfx/<OFFSET>.png (7 hex digits, the ECD
block offset as in docs/re/graphics.md), same size as the original, drawn only in the colours of its palette.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import romwrite  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
GFX = ROOT / "gfx"
ARC = 0x0E7FA4          # archive 0: every ECD block


def archive_words(rom):
    """-> {block offset: [ROM offset of each archive word pointing at it]}."""
    n = struct.unpack_from("<I", rom, ARC)[0] // 4
    out = {}
    for i in range(n):
        w = ARC + 4 * i
        out.setdefault(ARC + struct.unpack_from("<I", rom, w)[0], []).append(w)
    return out


def blocks(rom):
    return ecd.scan(rom)


def palette_for(rom, off, bl=None):
    """-> (list of RGB, PLT offset): the first PLT block after IMG block `off` (the game stores them in pairs)."""
    bl = bl or blocks(rom)
    i = [b[0] for b in bl].index(off)
    for j in range(i + 1, min(i + 4, len(bl))):
        if bl[j][3] == "PLT":
            raw = ecd.decompress(rom, bl[j][0])[0]
            n = struct.unpack_from("<H", raw, 4)[0] or 16
            cols = []
            for k in range(min(n, 16)):
                v = struct.unpack_from("<H", raw, 8 + 2 * k)[0] if 10 + 2 * k <= len(raw) else 0
                cols.append(((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8))
            return cols, bl[j][0]
    raise ValueError(f"no PLT after {off:07X}")


def indices(raw):
    """IMG payload (4bpp) -> (w px, h px, list of palette indices row-major)."""
    flag, w, h = raw[4], raw[5], raw[6]
    if flag != 0:
        raise ValueError("only 4bpp IMG blocks are handled")
    data = raw[8:]
    W, H = w * 8, h * 8
    px = [0] * (W * H)
    for t in range(w * h):
        tx, ty = t % w, t // w
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                px[(ty * 8 + y) * W + tx * 8 + x] = b >> 4 if x & 1 else b & 15
    return W, H, px


def to_png(raw, pal):
    W, H, px = indices(raw)
    img = Image.new("RGB", (W, H))
    img.putdata([pal[c] if c < len(pal) else (255, 0, 255) for c in px])
    return img


def from_png(path, raw, pal):
    """Edited PNG -> new IMG payload (same header). A colour used by several indices keeps the original pixel's
    index where that colour matches it, else takes the first index with that colour."""
    W, H, orig = indices(raw)
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        raise ValueError(f"{path.name}: {img.size} but the block is {W}x{H}")
    first = {}
    for i, c in enumerate(pal):
        first.setdefault(c, i)
    new = []
    bad = set()
    for k, c in enumerate(img.getdata()):
        o = orig[k]
        if o < len(pal) and pal[o] == c:
            new.append(o)
        elif c in first:
            new.append(first[c])
        else:
            bad.add(c)
            new.append(0)
    if bad:
        raise ValueError(f"{path.name}: colours not in the palette: {sorted(bad)[:6]}")
    w = W // 8
    out = bytearray(raw[:8])
    for t in range((W // 8) * (H // 8)):
        tx, ty = t % w, t // w
        for y in range(8):
            for x in range(0, 8, 2):
                p = (ty * 8 + y) * W + tx * 8 + x
                out.append(new[p] | new[p + 1] << 4)
    out += raw[len(out):]   # trailing bytes past the tiles, if any
    return bytes(out)


def edits():
    return sorted(GFX.glob("[0-9A-F]" * 7 + ".png"))


def apply(rom, out, free, log=None, limit=None):
    """Write every gfx/*.png into `out`. -> next free offset (16-aligned). `rom` = original image."""
    if not edits():
        return free
    bl = blocks(rom)
    starts = sorted(b[0] for b in bl)
    words = archive_words(rom)
    for path in edits():
        off = int(path.stem, 16)
        raw = ecd.decompress(rom, off)[0]
        pal, _ = palette_for(rom, off, bl)
        new = from_png(path, raw, pal)
        if new == raw:
            continue
        blob = ecd.compress(new)
        nxt = starts[starts.index(off) + 1]
        if len(blob) <= nxt - off:
            romwrite.put(log, out, off, blob, f"gfx {path.stem}")
            continue
        if limit is not None and free + len(blob) > limit:
            raise ValueError(f"gfx {path.stem}: no free space for {len(blob)} bytes")
        romwrite.put(log, out, free, blob, f"gfx {path.stem} (moved)")
        for w in words[off]:
            romwrite.put(log, out, w, struct.pack("<I", free - ARC), f"gfx {path.stem} archive word")
        free = (free + len(blob) + 15) & ~15
    return free


def main(argv):
    rom = ROM.read_bytes()
    if len(argv) >= 2 and argv[0] == "export":
        d = ROOT / "work" / "gfx" / "orig"
        d.mkdir(parents=True, exist_ok=True)
        bl = blocks(rom)
        for a in argv[1:]:
            off = int(a, 16)
            raw = ecd.decompress(rom, off)[0]
            pal, po = palette_for(rom, off, bl)
            img = to_png(raw, pal)
            img.save(d / f"{off:07X}.png")
            img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(d / f"{off:07X}_x4.png")
            print(f"{off:07X}: {img.width}x{img.height}, palette {po:07X}: "
                  + " ".join("%d=%02x%02x%02x" % ((i,) + c) for i, c in enumerate(pal)))
        return 0
    if argv == ["check"]:
        bl = blocks(rom)
        for path in edits():
            off = int(path.stem, 16)
            raw = ecd.decompress(rom, off)[0]
            new = from_png(path, raw, palette_for(rom, off, bl)[0])
            blob = ecd.compress(new)
            print(f"{path.stem}: {'unchanged' if new == raw else 'edited'}, {len(blob)} bytes compressed")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
