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

# u16 map (SCR) entries fixed alongside the art: (ROM offset, original words, English words, why). Written by
# apply() whenever gfx/ holds a PNG; the original words are checked so a wrong offset fails the build.
# Field menu atlas 01E30D4 (entries = atlas row*32+col, 0x1FF = blank tile; tools/gfx_text.py draws the labels):
# "Save" and "Sort" fit 4 tiles, which frees 1,21 for the bar's Database button (the JP map used the frame-only 4,12,
# also the submenus' bottom frame) and 2,13 / 2,18 to widen Keywords to 6 tiles.
MAP_PATCHES = [
    (0x1E365A, [0x08C], [0x035], "menu bar SCR 01E3644: Database bottom col 1 -> 1,21"),
    (0x1E372C, [0x040, 0x041, 0x042, 0x043, 0x044, 0x035], [0x1FF, 0x040, 0x041, 0x042, 0x043, 0x1FF],
     "System submenu SCR 01E3724 row 0: Save in 2,0-2,3"),
    (0x1E3794, [0x04D, 0x04E, 0x04F, 0x050, 0x051, 0x052], [0x1FF, 0x04E, 0x04F, 0x050, 0x051, 0x1FF],
     "Items submenu SCR 01E3774 row 2: Sort in 2,14-2,17"),
    (0x1E38DC, [0x1FF, 0x088, 0x089, 0x08A, 0x08B, 0x1FF], [0x04D, 0x088, 0x089, 0x08A, 0x08B, 0x052],
     "Database submenu SCR 01E38A4 row 4: Keywords in 2,13 4,8-4,11 2,18"),
]
# PDA timetable palette status line "月曜日 1時間目 = [icon]" (PAT at 0x22F194, block 022CF64; entries u16 size,
# s16 x, s16 y, u16 tile, screen x = 120 + x) -> "Mon, period 1 = [icon]": weekday frames (Mon..Sat) move the
# weekday to x84 and the 曜日 16x16 piece (now ",") to x100; digit frames (1..7) move the 時間目 32x16 piece (now
# "period") to x106, the digit to x133 and "=" to x141 (the 時間目 and 曜日 8x16 tails are blank).
TT_DAYS = [0x22F246, 0x22F260, 0x22F27A, 0x22F294, 0x22F2AE, 0x22F2C8]
TT_DIGITS = [0x22F2E2 + 0x22 * n for n in range(7)]


def tt_patches(rom):
    out = []
    for k, f in enumerate(TT_DAYS):
        for i in range(3):
            e = f + 2 + 8 * i
            tile = struct.unpack_from("<H", rom, e + 6)[0] & 0x3FF
            new = {128 + 2 * k: -36, 140: -20}.get(tile)
            if new is not None:
                old = struct.unpack_from("<h", rom, e + 2)[0]
                out.append((e + 2, [old & 0xFFFF], [new & 0xFFFF], f"timetable weekday frame {k}: tile {tile} x"))
    for n, f in enumerate(TT_DIGITS):
        for i in range(4):
            e = f + 2 + 8 * i
            tile = struct.unpack_from("<H", rom, e + 6)[0] & 0x3FF
            new = {144 + n: 13, 143: 21, 151: -14}.get(tile)
            if new is not None:
                old = struct.unpack_from("<h", rom, e + 2)[0]
                out.append((e + 2, [old & 0xFFFF], [new & 0xFFFF], f"timetable digit frame {n}: tile {tile} x"))
    if len(out) != 6 * 2 + 7 * 3:
        raise ValueError(f"timetable PAT: {len(out)} entries found, expected 33")
    return out

# Title screen planet name (block 0449734, OBJ 2D, OBJ tile n = block tile n). Sprite frames 3-12 of the title's
# PAT animation at 0x44BF24 (u32 offsets from it at +8) each hold 8 OAM entries (u16 size code | 0x2000, s16 x,
# s16 y, u16 tile | pal << 12); the name is a 32x8 piece at x 8, a second piece at x 40 and the bar's end cap
# (tile 413) at x 48, all 40 px bars in JP. English: (frame, name, atlas tile row, first column, tiles): a 32x8 +
# 8x8 / 16x8 / 32x8 piece, the cap at x 8 + 8 * tiles; 7 tiles = two 32x8 pieces whose last tile is left
# transparent under the cap. tools/gfx_text.py paints the runs.
TITLE_ANIM = 0x44BF24
TITLE_NAMES = [
    (3, "Terioranus", 10, 8, 6), (4, "Sigmazon", 10, 20, 5), (5, "Capuchipean", 10, 0, 7),
    (6, "Bisaios", 10, 25, 5), (7, "Jornaturn", 10, 14, 6), (8, "Parmoon", 11, 0, 5), (9, "Plutario", 11, 5, 5),
    (10, "Mercurie", 11, 10, 5), (11, "Byjupiter", 11, 15, 5), (12, "Zaurak", 11, 20, 5),
]
SIZE_CODE = {5: 0x00, 6: 0x41, 7: 0x52}   # second piece: 8x8, 16x8, 32x8


def title_patches(rom):
    """MAP_PATCHES-style rows for the planet name entries of title frames 3-12."""
    out = []
    for frame, name, row, col, n in TITLE_NAMES:
        p = TITLE_ANIM + struct.unpack_from("<I", rom, TITLE_ANIM + 8 + 4 * frame)[0]
        if struct.unpack_from("<h", rom, p)[0] != 8:
            raise ValueError(f"title frame {frame}: expected 8 OAM entries")
        start = 32 * row + col
        ents = {struct.unpack_from("<h", rom, p + 4 + 8 * i)[0]: p + 2 + 8 * i for i in range(8)}
        for x, attr, nx, tile in ((8, None, 8, start), (40, SIZE_CODE[n], 40, start + 4), (48, None, 8 + 8 * n, 413)):
            e = ents[x]
            old = list(struct.unpack_from("<4H", rom, e))
            new = [old[0] if attr is None else (old[0] & 0xFF00) | attr, nx, old[2], (old[3] & 0xFC00) | tile]
            if x == 48 and old[3] & 0x3FF != 413:
                raise ValueError(f"title frame {frame}: no end cap at x 48")
            out.append((e, old, new, f"title frame {frame} {name}: piece at x {x}"))
    return out


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
    title = title_patches(rom) if (GFX / "0449734.png").exists() else []
    title += tt_patches(rom) if (GFX / "022CF64.png").exists() else []
    for off, old, new, why in MAP_PATCHES + title:
        if list(struct.unpack_from(f"<{len(old)}H", rom, off)) != old:
            raise ValueError(f"gfx map patch {off:#x}: original words differ ({why})")
        romwrite.put(log, out, off, struct.pack(f"<{len(new)}H", *new), f"gfx map {why}")
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
