"""hud.py: the field HUD's Dyna status word (けんこう / くうふく / びょうき -> Healthy / Hungry / Sick).

    python -X utf8 tools/hud.py          # writes gfx/01E5464.png from the original block

Block 01E5464 is a raw IMG (archive index 0x70B, 10x5 tiles), copied to BG VRAM 0xEDC0 as a 2D rect with a
32-tile row stride, so the field SCRs address it as 32 * row + col (base tile 0x36E). The status word is one of
three raw 5x1 SCRs, archive 0x70F + status (code 0x08043FCA: 0 healthy, 1 hungry, 2 sick), whose tiles 0x81-0x89
(row 4, cols 1-9) held the nine kana. English needs the same nine tiles: a shared "H" tile, "ealthy" (3 tiles),
"ungry" (3), "Sick" (2); gfx.HUD_PATCHES re-lays SCRs 0x710 / 0x711 to match (tile 0 = blank). Drawn in the kana's
style: ink index 1 with a shadow (index 15) one pixel below; vwf8 glyphs, 'y' narrowed to 3 px so Healthy fits.
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
import vwf  # noqa: E402

BLOCK = 0x1E5464
INK, SHADOW = 1, 15
ROW = 4                      # block tile row of the kana
Y3 = [0, 0, 0b101, 0b101, 0b101, 0b011, 0b001, 0b110]   # 3 px wide 'y' (rows, bit 2 = left column)
# (text, first block column, x offset inside the run): each run is drawn left to right from that tile
RUNS = [("H", 1, 3), ("ealthy", 2, 0), ("ungry", 5, 0), ("Sick", 8, 1)]


def ink(text):
    """-> set of (x, y) ink pixels of `text` in vwf8 with the narrow 'y', and the width."""
    f, x, out = vwf.font(), 0, set()
    for ch in text:
        if ch == "y":
            out |= {(x + gx, gy) for gy, bits in enumerate(Y3) for gx in range(3) if bits & (4 >> gx)}
            x += 4
            continue
        adv, rows = f[ch]
        out |= {(x + gx, gy) for gy, bits in enumerate(rows) for gx in range(adv - 1) if bits & (0x80 >> gx)}
        x += adv
    return out, x - 1


def draw():
    rom = gfx.ROM.read_bytes()
    W, H, px = gfx.indices(gfx.load(rom, BLOCK))
    pal, _ = gfx.palette_for(rom, BLOCK)
    top = ROW * 8
    for y in range(top, top + 8):
        for x in range(8, 80):
            px[y * W + x] = 0
    for text, col, dx in RUNS:
        pts, width = ink(text)
        x0 = col * 8 + dx
        tiles = (dx + width + 7) // 8
        limit = x0 - dx + 8 * tiles
        for x, y in pts:
            if x0 + x >= limit or y > 7:
                raise ValueError(f"{text!r} runs past its {tiles} tiles")
            px[(top + y) * W + x0 + x] = INK
        for x, y in pts:
            if y + 1 < 8 and (x, y + 1) not in pts:
                px[(top + y + 1) * W + x0 + x] = SHADOW
    img = Image.new("RGB", (W, H))
    img.putdata([pal[c] for c in px])
    return img


# Field pause (START): raw IMG 01F1994 (archive 0x772, OBJ, 32x2 tiles), ポーズ in cols 29-31 (x 232-255, 16 px
# high), shown as six 8x8 OBJs with the top row 2 px right of the bottom row (italic). "Pause" in vwf8 rows doubled,
# green fill (15) with a light cyan outline (9) as the kana; 'P' narrowed to 3 px so text + outline fit 24 px.
PAUSE = 0x1F1994
P3 = [0b111, 0b101, 0b101, 0b111, 0b100, 0b100, 0b100, 0]


def draw_pause():
    rom = gfx.ROM.read_bytes()
    W, H, px = gfx.indices(gfx.load(rom, PAUSE))
    pal, _ = gfx.palette_for(rom, PAUSE)
    f, x, pts = vwf.font(), 0, set()
    for ch in "Pause":
        if ch == "P":
            pts |= {(x + gx, gy) for gy, bits in enumerate(P3) for gx in range(3) if bits & (4 >> gx)}
            x += 4
            continue
        adv, rows = f[ch]
        pts |= {(x + gx, gy) for gy, bits in enumerate(rows) for gx in range(adv - 1) if bits & (0x80 >> gx)}
        x += adv
    fill = {(1 + gx, 1 + 2 * gy + k) for gx, gy in pts for k in (0, 1)}
    edge = {(a + dx, b + dy) for a, b in fill for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - fill
    x0 = 232
    if max(a for a, _ in edge) > 23 or max(b for _, b in edge) > 15:
        raise ValueError("Pause runs past its 3x2 tiles")
    for y in range(16):
        for xx in range(x0, x0 + 24):
            px[y * W + xx] = 0
    for (a, b), c in [(p, 9) for p in edge] + [(p, 15) for p in fill]:
        px[b * W + x0 + a] = c
    img = Image.new("RGB", (W, H))
    img.putdata([pal[c] for c in px])
    return img


def main():
    for off, fn in ((BLOCK, draw), (PAUSE, draw_pause)):
        out = gfx.GFX / f"{off:07X}.png"
        fn().save(out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
