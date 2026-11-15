"""title_frames.py: draw the title screen's planet-name sprite frames (3-12) of a ROM, as the game lays them out.

    python -X utf8 tools/title_frames.py [ROM] [--out work/qa/gfx_en/title_frames.png]

Reads block 0449734 (OBJ 2D, block tile n = OBJ tile n) and the PAT frames at tools/gfx.py TITLE_ANIM, places each
frame's 8x8-row pieces (x >= 8: the name and its end cap, plus the emblem label and planet symbol at x < 8) on a
240 px row with screen x = 120 + x, and stacks the 10 rows at 4x. The emblem label is OBJ x 64-111, the name from 128.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SHAPES = [[(1, 1), (2, 2), (4, 4), (8, 8)], [(2, 1), (4, 1), (4, 2), (8, 4)], [(1, 2), (1, 4), (2, 4), (4, 8)]]


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    rom_path = Path(args[0]) if args else ROOT / "build" / "dynadevice_blue_en.gba"
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ROOT / "work" / "qa" / "gfx_en" / "title_frames.png"
    rom = rom_path.read_bytes()
    raw = ecd.decompress(rom, 0x449734)[0]
    pal, _ = gfx.palette_for(gfx.ROM.read_bytes(), 0x449734)
    W, H, px = gfx.indices(raw)
    img = Image.new("RGB", (240, 24 * 10), (40, 40, 40))
    for k, frame in enumerate(range(3, 13)):
        p = gfx.TITLE_ANIM + struct.unpack_from("<I", rom, gfx.TITLE_ANIM + 8 + 4 * frame)[0]
        n = struct.unpack_from("<h", rom, p)[0]
        for i in range(n):
            attr, x, y, tw = struct.unpack_from("<HhhH", rom, p + 2 + 8 * i)
            w, h = SHAPES[(attr >> 6) & 3][(attr >> 4) & 3]
            hflip = attr & 0x100
            t0 = tw & 0x3FF
            for ty in range(h):
                for tx in range(w):
                    r, c = divmod(t0 + 32 * ty + tx, 32)
                    for yy in range(8):
                        for xx in range(8):
                            v = px[(8 * r + yy) * W + 8 * c + xx]
                            if not v:
                                continue
                            sx = 8 * (w - 1 - tx) + (7 - xx) if hflip else 8 * tx + xx
                            X, Y = 120 + x + sx, 24 * k + 4 + y - 0x10 + 8 * ty + yy
                            if 0 <= X < 240 and 24 * k <= Y < 24 * k + 24:
                                img.putpixel((X, Y), pal[v])
    out.parent.mkdir(parents=True, exist_ok=True)
    img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(out)
    print(out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
