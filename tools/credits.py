"""credits.py: the staff roll (mode 22) in English: charset gfx/0432534.png and a new sprite-frame block (PAT).

    python -X utf8 tools/credits.py           # writes gfx/0432534.png (and work/gfx/en/0432534_x4.png)
    python -X utf8 tools/credits.py --show    # also work/gfx/en/credits_frames.png: every card as the game lays it

The roll draws its words as OBJ sprites: block 0432534 (IMG 224x48, 8x16 kana glyphs: tile n on top of n + 32,
2D OBJ mapping at VRAM 0x10000) and the PAT at ROM 0x432D44 (archive-0 word 0x0EFEB4; 11 frames = 11 cards,
one 8x16 sprite per kana, x/y from an anchor at screen 120,51). English needs ~400 sprites, the old PAT holds 274
in 0x8E0 bytes, so gfx.apply writes pat_blob() into free space and repoints the archive word. Each English letter
is one 8x16 sprite placed at its VWF pen position (fonts/vwf8.txt), so the 7 px font keeps its proportional
spacing. Names: Western order, Hepburn without macrons (D1, D2). docs/re/graphics.md "Staff roll".
"""
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402
import vwf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = 0x432534
PAT = 0x432D44
PLT = 0x432D14            # the charset's palette block
COLS = 28                 # charset width in tiles
INK = 1
SHADOW = 4                # black, 1 px down-right: the last card sits on the bright picture
GLYPH_Y = 6               # cell row of the font's row 0 (kana ink sits in rows 5-14)
RIGHT = 112               # rightmost x (anchor-relative) a line may reach: screen 232
SIZE_8X16 = 0x2084        # the old PAT's size word for an 8x16 sprite
SIZE_16X16 = 0x2015
COPY = (25, 4)            # (col, row) of the original 16x16 copyright mark, kept as it is

# One entry per PAT frame, in frame order: lines top to bottom; the first line of a staff card is the job.
CARDS = [
    ["Dyna Device Staff"],
    ["Character Design", "Haine Yamanekoya"],
    ["Game Design", "Tatsuya Akaishi"],
    ["Programming", "Katsutoshi Sato", "Ippei Horii", "Takahiro Nishiyama", "Norihisa Takabatake"],
    ["Graphics", "Akira Katagi", "Naoko Katagi", "Yuki Shukuzawa"],
    ["Assistants", "Satomi Hoshino", "Junko Sugimoto"],
    ["Special Thanks", "Yoshinori Yamagishi", "Tetsuma Yoshida", "Katsumi Miyashita", "Hiroyuki Arai"],
    ["Director", "Koichi Kobayashi"],
    ["Executive Producer", "Shuhei Iida"],
    ["©2002 Smilesoft"],
    ["Sound", "Motoharu Yoshihira", "Ushio Otsuki", "Akihiro Juichiya"],
]
CENTRED = {9}             # the copyright card is centred on the old line's centre


def frames_of(rom):
    n = struct.unpack_from("<I", rom, PAT + 4)[0]
    out = []
    for k in range(n):
        f = PAT + struct.unpack_from("<I", rom, PAT + 8 + 4 * k)[0]
        cnt = struct.unpack_from("<h", rom, f)[0]
        out.append([struct.unpack_from("<Hhhh", rom, f + 2 + 8 * e) for e in range(cnt)])
    return out


def glyphs():
    """Characters to draw (the copyright mark is the old 16x16 one) -> {char: slot}."""
    chars = sorted({c for card in CARDS for line in card for c in line} - {" ", "©"})
    slots = [(r, c) for r in range(3) for c in range(COLS) if not (r == 2 and c in (COPY[0], COPY[0] + 1))]
    if len(chars) > len(slots):
        raise ValueError(f"credits: {len(chars)} glyphs, {len(slots)} slots")
    return dict(zip(chars, slots))


def tile_of(slot):
    r, c = slot
    return 64 * r + c


def advance(ch, font):
    return font[ch][0]


def layout():
    """-> [[(x, y, tile, size word)]] per frame, from CARDS and the old frames' line rows and left edges."""
    rom = gfx.ROM.read_bytes()
    old = frames_of(rom)
    if len(old) != len(CARDS):
        raise ValueError(f"credits: PAT has {len(old)} frames, CARDS {len(CARDS)}")
    font = vwf.font()
    g = glyphs()
    out = []
    for k, (card, ents) in enumerate(zip(CARDS, old)):
        rows = sorted({y for size, x, y, t in ents if size == SIZE_8X16})
        left = min(x for size, x, y, t in ents)
        right = max(x + (16 if size == SIZE_16X16 else 8) for size, x, y, t in ents)
        n = len(card)
        if n == len(rows):
            ys = rows
        else:
            mid = (rows[0] + rows[-1]) // 2
            ys = [mid - 8 * (n - 1) + 16 * i for i in range(n)]
        widths = [sum(16 if c == "©" else advance(c, font) for c in line) - 1 for line in card]
        indent = [0] + [8] * (n - 1)
        block = max(w + i for w, i in zip(widths, indent))
        if k in CENTRED:
            x0 = (left + right) // 2 - block // 2
        else:
            x0 = left if left + block <= RIGHT else RIGHT - block
        sprites = []
        for line, y, ind in zip(card, ys, indent):
            x = x0 + ind
            for c in line:
                if c == "©":
                    sprites.append((x, y - 1, 32 * COPY[1] + COPY[0], SIZE_16X16))
                    x += 16
                    continue
                if c != " ":
                    sprites.append((x, y, tile_of(g[c]), SIZE_8X16))
                x += advance(c, font)
        out.append(sprites[::-1])   # right to left (as the old frames): each letter on top of its left neighbour's shadow
    return out


def pat_blob():
    frames = layout()
    head = 8 + 4 * len(frames)
    body = bytearray()
    offs = []
    for sp in frames:
        offs.append(head + len(body))
        body += struct.pack("<h", len(sp))
        for x, y, t, size in sp:
            body += struct.pack("<Hhhh", size, x, y, t)
    return b"PAT\0" + struct.pack("<I", len(frames)) + b"".join(struct.pack("<I", o) for o in offs) + bytes(body)


def charset_png():
    rom = gfx.ROM.read_bytes()
    raw = ecd.decompress(rom, IMG)[0]
    pal, _ = gfx.palette_for(rom, IMG, [(IMG, 0, 0, "IMG"), (PLT, 0, 0, "PLT")])   # skips the slow ecd.scan
    W, H, px = gfx.indices(raw)
    new = [0] * (W * H)
    cx, cy = COPY[0] * 8, COPY[1] * 8
    for y in range(cy, cy + 16):            # keep the copyright mark
        for x in range(cx, cx + 16):
            new[y * W + x] = px[y * W + x]
    font = vwf.font()
    for ch, (r, c) in glyphs().items():
        adv, rows = font[ch]
        ink = {(gx, gy) for gy, bits in enumerate(rows) for gx in range(adv - 1) if bits & (0x80 >> gx)}
        for gx, gy in ink | {(x + 1, y + 1) for x, y in ink}:
            new[(16 * r + GLYPH_Y + gy) * W + 8 * c + gx] = INK if (gx, gy) in ink else SHADOW
    img = Image.new("RGB", (W, H))
    img.putdata([pal[i] for i in new])
    return img


def show(img):
    """Every frame drawn from the new charset, 2 columns, anchor at 120,51 of a 240x100 card."""
    tiles = {}
    W = img.width // 8
    clear = img.getpixel((0, 0))   # index 0 (transparent in game): the top-left cell is blank

    def tile(t):
        if t not in tiles:
            r, c = divmod(t, 32)
            tiles[t] = img.crop((8 * c, 8 * r, 8 * c + 8, 8 * r + 8)) if c < W else Image.new("RGB", (8, 8))
        return tiles[t]
    fr = layout()
    sheet = Image.new("RGB", (480, 100 * ((len(fr) + 1) // 2)), (20, 20, 40))
    for k, sp in enumerate(fr):
        card = Image.new("RGB", (240, 100), (40, 40, 90))
        for x, y, t, size in sp:
            w = 2 if size == SIZE_16X16 else 1
            for rr in range(2):
                for cc in range(w):
                    tl = tile(t + 32 * rr + cc)
                    mask = Image.new("L", (8, 8))
                    mask.putdata([0 if p == clear else 255 for p in tl.getdata()])
                    card.paste(tl, (120 + x + 8 * cc, 51 + y + 8 * rr), mask)
        card.paste((255, 0, 0), (0, 99, 240, 100))
        sheet.paste(card, (240 * (k % 2), 100 * (k // 2)))
    return sheet


def main(argv):
    img = charset_png()
    out = ROOT / "gfx" / f"{IMG:07X}.png"
    img.save(out)
    en = ROOT / "work" / "gfx" / "en"
    en.mkdir(parents=True, exist_ok=True)
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(en / f"{IMG:07X}_x4.png")
    blob = pat_blob()
    print(f"{out.relative_to(ROOT)}: {len(glyphs())} glyphs; PAT {len(blob)} bytes, "
          f"{sum(len(f) for f in layout())} sprites, most in one frame {max(len(f) for f in layout())}")
    if "--show" in argv:
        s = show(img)
        s.resize((s.width * 2, s.height * 2), Image.NEAREST).save(en / "credits_frames.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
