"""gfx_text.py: draw English labels into the game's tile atlases -> gfx/<OFFSET>.png (read by gfx.apply at build).

    python -X utf8 tools/gfx_text.py            # (re)writes every gfx/<OFFSET>.png listed in ATLASES
    python -X utf8 tools/gfx_text.py --zoom     # also work/gfx/en/<OFFSET>_x4.png to look at

An atlas label is a strip of 8x16 px button columns: each column is a (top tile, bottom tile) pair of atlas tiles,
in the order the game's map puts them on screen (docs/re/graphics.md "Field menu bar"). The Japanese ink
(palette index INK) is cleared from rows 2-11 of the strip, then the English is drawn with fonts/vwf8.txt in the
same index, glyph rows 0-6 at strip y 3-9 (descenders at y 10), centred in the strip's text span.
Maps the game reads from ROM data are fixed with gfx.WORD_PATCHES (e.g. a button that used a frame-only tile).
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402
import vwf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK = 1
TEXT_Y = 3           # strip row of glyph row 0
CLEAR = range(2, 12)  # strip rows that hold label ink (rows 0-1 and 12-13 are the button frame)


def tiles(row, c0, c1):
    """Atlas tiles (row, c0..c1) as a list."""
    return [(row, c) for c in range(c0, c1 + 1)]


def strip(top, bottom):
    return list(zip(top, bottom))


def mid(tl):
    """A submenu row: blank, 4 middle tiles, blank (the SCR rows' 0x1FF columns)."""
    return [None] + tl + [None]


# Field menu (BG0, block 01E30D4). Bar maps 01E35C4-01E3644: caps 0,0 / 0,5 are blank frame shared by the three
# 6-column buttons, so System/Items/Party draw in their 4 middle columns. Submenu maps 01E3724-01E38A4: 6 tiles a
# row, one 8 px tile tall, the words in atlas rows 2-4; gfx.MAP_PATCHES re-lays rows (Save, Sort, Keywords).
MENU_BAR = 0x1E30D4
ATLASES = {
    MENU_BAR: {
        # 1,21 gets the frame-only tile 4,12 (bottom col 1 of a 6-col button) and becomes the Database button's.
        "copy": [((4, 12), (1, 21))],
        "blank": [(2, 4)],   # no longer on any map (Save fits 2,0-2,3)
        "labels": [
            ("System", strip(tiles(0, 1, 4), tiles(1, 1, 4))),
            ("Items", strip(tiles(0, 6, 9), tiles(1, 6, 9))),
            ("Party", strip(tiles(0, 10, 13), tiles(1, 10, 13))),
            ("Residents", strip(tiles(0, 14, 19), tiles(1, 14, 19))),
            ("Database", strip(tiles(0, 20, 23) + [(2, 22), (2, 23)],
                               tiles(1, 20, 23) + [(3, 22), (3, 23)])),
        ],
        "rows": [
            ("Save", mid(tiles(2, 0, 3))),
            ("Battle Anim", tiles(4, 18, 22) + [(3, 20)]),
            ("Quit", mid(tiles(2, 5, 8))),
            ("Use", mid(tiles(2, 9, 12))),
            ("Sort", mid(tiles(2, 14, 17))),
            ("Discard", mid(tiles(2, 19, 21) + [(3, 21)])),
            ("Status", mid(tiles(3, 0, 3))),          # Party and Residents
            ("Equip", mid(tiles(3, 6, 9))),           # Party and Residents
            ("Send Home", tiles(3, 10, 15)),
            ("Release", mid(tiles(3, 16, 19))),       # Party and Residents
            ("Map", mid(tiles(4, 0, 3))),
            ("Dyna", mid(tiles(4, 4, 7))),
            ("Device", mid([(3, 4), (3, 5), (4, 16), (4, 17)])),
            ("Keywords", [(2, 13)] + tiles(4, 8, 11) + [(2, 18)]),
        ],
    },
    # Profile form (BG2, block 020EB44, ink index 4): one-tile-high labels set into the field lines (line at tile
    # y 2, label tiles between 6,29..6,31 frame tiles; tools/bgmap.py on scenes form / form_scroll). The phone
    # labels share their last 3 tiles (ばんごう 8,11-13): "Home" / "Mobile" end flush right, "Tel." starts flush left.
    0x20EB44: {
        "ink": 4,
        "rows": [
            ("Name", tiles(7, 0, 2)),
            ("Nickname", tiles(7, 3, 7)),
            ("Gender", tiles(8, 0, 3)),
            ("Address", tiles(8, 4, 7), "tight"),
            ("Home", tiles(8, 8, 10), "right"),
            ("Tel.", tiles(8, 11, 13), "left"),
            ("Mobile", tiles(8, 14, 17), "right"),
            ("Email", tiles(8, 18, 23)),
            ("Birthday", tiles(8, 24, 28)),
            ("Blood Type", tiles(7, 25, 30)),
        ],
    },
}


class Atlas:
    def __init__(self, rom, off):
        self.raw = ecd.decompress(rom, off)[0]
        self.pal, _ = gfx.palette_for(rom, off)
        self.W, self.H, self.px = gfx.indices(self.raw)

    def get(self, t, x, y):
        r, c = t
        return self.px[(r * 8 + y) * self.W + c * 8 + x]

    def set(self, t, x, y, v):
        r, c = t
        if (r + 1) * 8 > self.H or (c + 1) * 8 > self.W:
            raise ValueError(f"tile {t} outside the {self.W}x{self.H} atlas")
        self.px[(r * 8 + y) * self.W + c * 8 + x] = v

    def copy(self, src, dst):
        for y in range(8):
            for x in range(8):
                self.set(dst, x, y, self.get(src, x, y))

    def image(self):
        img = Image.new("RGB", (self.W, self.H))
        img.putdata([self.pal[c] for c in self.px])
        return img


def strip_cell(columns, x, y):
    """Strip pixel (x, y) -> (tile, tile x, tile y)."""
    top, bottom = columns[x // 8]
    return (top if y < 8 else bottom), x % 8, y % 8


def clear_strip(atlas, columns):
    for y in CLEAR:
        for x in range(len(columns) * 8):
            t, tx, ty = strip_cell(columns, x, y)
            if atlas.get(t, tx, ty) == INK:
                atlas.set(t, tx, ty, 0)


def draw_text(atlas, text, w, top, cell, align="centre", ink=INK):
    """Draw `text` in a span `w` px wide (1 px margin each side; "left"/"right" hug that margin, for a word that
    continues in the next span); cell(x, y) -> (tile, tx, ty) or raises for a blank column."""
    tw = vwf.width(text) - 1
    room = w if align == "tight" else w - 2   # "tight": no margin, for a label set off by a gap in its frame
    if tw > room:
        raise ValueError(f"{text!r} is {tw} px, the label holds {room}")
    x = {"left": 1, "right": w - 1 - tw, "tight": (w - tw) // 2}.get(align, (w - tw + 1) // 2)
    font = vwf.font()
    for ch in text:
        adv, rows = font[ch]
        for gy, bits in enumerate(rows):
            for gx in range(adv - 1):
                if bits & (0x80 >> gx):
                    t, tx, ty = cell(x + gx, top + gy)
                    atlas.set(t, tx, ty, ink)
        x += adv


def row_cell(text, columns):
    def cell(x, y):
        t = columns[x // 8]
        if t is None:
            raise ValueError(f"{text!r} reaches blank column {x // 8} of its row")
        return t, x % 8, y
    return cell


def render(rom, off):
    spec = ATLASES[off]
    a = Atlas(rom, off)
    for src, dst in spec.get("copy", []):
        a.copy(src, dst)
    # clear every label's tiles before drawing any: a freed tile can move to another label (2,13 -> Keywords)
    for t in spec.get("blank", []):
        for y in range(8):
            for x in range(8):
                a.set(t, x, y, 0)
    ink = spec.get("ink", INK)
    for _, columns in spec.get("labels", []):
        clear_strip(a, columns)
    for _, columns, *_ in spec.get("rows", []):
        for t in filter(None, columns):
            for y in range(8):
                for x in range(8):
                    if a.get(t, x, y) == ink:
                        a.set(t, x, y, 0)
    for text, columns in spec.get("labels", []):
        draw_text(a, text, len(columns) * 8, TEXT_Y, lambda x, y, c=columns: strip_cell(c, x, y))
    for text, columns, *align in spec.get("rows", []):   # caps rows 0-6, descenders row 7
        draw_text(a, text, len(columns) * 8, 0, row_cell(text, columns), *(align or ["centre"]), ink=ink)
    return a.image()


def main(argv):
    rom = gfx.ROM.read_bytes()
    gfx.GFX.mkdir(exist_ok=True)
    for off in ATLASES:
        img = render(rom, off)
        path = gfx.GFX / f"{off:07X}.png"
        img.save(path)
        spec = ATLASES[off]
        print(f"{path.relative_to(ROOT)}: {len(spec.get('labels', [])) + len(spec.get('rows', []))} labels")
        if "--zoom" in argv:
            z = ROOT / "work" / "gfx" / "en"
            z.mkdir(parents=True, exist_ok=True)
            img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(z / f"{off:07X}_x4.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
