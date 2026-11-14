"""edge.py: measure a window's text budget from a shot (phase 5 width gate).

    python -X utf8 tools/edge.py SHOT.png COL ROW0 ROW1 [--tol 60]

The window's text starts at map cell COL (x = COL*8, size-3 cells, as tools/lua/markerlog.lua logs it) on rows
ROW0..ROW1. A frame is a vertical line: the first x right of the start where the pixels of every scanline from
ROW0*8 to ROW1*8+7 have (nearly) one colour that differs from the background at the start by more than --tol
(|dR|+|dG|+|dB|). Text glyphs never fill a whole column over several rows, so they don't stop the scan.
Prints the edge x and budget = edge - start. A list with no frame (items over a picture, a price column) has no
such line: read the next element's x off a zoomed crop (sheet.py --crop --zoom) instead.
"""
import argparse
import sys

from PIL import Image


def dist(a, b):
    return sum(abs(p - q) for p, q in zip(a, b))


def frame_edge(img, col, row0, row1, tol):
    px = img.load()
    x0 = col * 8
    ys = range(row0 * 8, row1 * 8 + 8)
    bg = px[max(x0 - 1, 0), ys[-1]][:3]
    for x in range(x0 + 1, img.width):
        cs = [px[x, y][:3] for y in ys]
        if max(dist(c, cs[0]) for c in cs) <= 12 and dist(cs[0], bg) > tol:
            return x0, x, cs[0]
    return x0, img.width, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("col", type=int)
    ap.add_argument("row0", type=int)
    ap.add_argument("row1", type=int)
    ap.add_argument("--tol", type=int, default=60)
    a = ap.parse_args()
    img = Image.open(a.shot).convert("RGB")
    x0, x, c = frame_edge(img, a.col, a.row0, a.row1, a.tol)
    print(f"col {a.col} rows {a.row0}-{a.row1}: start x {x0}, edge x {x} -> budget {x - x0} px (frame colour {c})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
