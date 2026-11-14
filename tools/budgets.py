"""budgets.py: write docs/re/budgets.tsv (string width budgets for tools/lint.py) from the window table below and
the marker-tour placements in docs/re/marks_p5.tsv (tools/marks.py --tsv on a tools/lua/markerlog.lua tour).

    python -X utf8 tools/budgets.py            # rewrite docs/re/budgets.tsv
    python -X utf8 tools/budgets.py --check    # exit 1 if the file is stale

Rows (lint takes the first match, so per-id rows come before the ranges):
  1. every string the tour drew: the smallest budget among the windows it was drawn in (WINDOW[size, col]);
  2. id ranges by content class (CLASSES) for the strings no tour reached yet.
Status column: measured (the window's frame or next element read off a shot, docs/re/windows.md) or guess.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKS = ROOT / "docs" / "re" / "marks_p5.tsv"
OUT = ROOT / "docs" / "re" / "budgets.tsv"

# (size, start col) -> (px, variant, status). Size-3 cells are 8 px: the text starts at x = col*8.
# Measured: tools/edge.py (vertical frame line) or a zoomed crop, on work/qa/p5_mk/<scene>/hold.png.
WINDOW = {
    (3, 1): (88, "description box (item, shop, sell, DB help): x 8, frame x 98", "measured"),
    (3, 2): (86, "field build menu (box inner x 104), team help (frame x 106), PDA schedule cells", "measured"),
    (3, 3): (104, "customize tree, deep level (frame x 133, 5 px margin as col 5)", "measured"),
    (3, 4): (64, "party status attack names (frame x 99), dyna shop names", "measured"),
    (3, 5): (88, "customize tree (frame x 133, 2 px margin)", "measured"),
    (3, 6): (64, "auction item names (upgrade mark at col 14)", "measured"),
    (3, 7): (58, "dyna shop card HP / mood (card inner x 114)", "measured"),
    (3, 8): (50, "resident map sector label (panel inner x 114)", "measured"),
    (3, 9): (32, "field build menu header: sector type (box inner x 104)", "measured"),
    (3, 13): (28, "customize level value (tree frame x 133)", "measured"),
    (3, 15): (72, "dynapad title (screen inner x 192)", "measured"),
    (3, 16): (80, "sell list names (price column at x 213), party Dyna name", "measured"),
    (3, 17): (70, "item menu list (count at x 209)", "measured"),
    (3, 18): (70, "kit list (count at col 27), keyword list (screen edge), dyna status", "measured"),
    (3, 19): (86, "card exchange panel (inner x 238), free-battle opponent (screen edge)", "measured"),
    (3, 20): (65, "resident map postal line (edge x 225), party equip names (frame x 226)", "measured"),
    (3, 21): (66, "shop list spec panel (frame x 236)", "measured"),
    (3, 22): (60, "get screen type panel (inner x 236), dyna status (frame x 239)", "measured"),
}

# (id, start col) -> window, where one column holds windows of different widths (shots: docs/re/windows.md).
ID_WINDOW = {
    ("t0B9944", 8): (141, "date prompt line (box inner x 205)", "measured"),
    ("t0B9418", 7): (48, "dynapad TRACK label (track number at x 104)", "measured"),
    ("t0BB1B8", 7): (74, "battle result name (count column at x 131)", "measured"),
    ("t0B2058", 13): (70, "tutorial team card name (Lv at x 176)", "measured"),
    ("t0B9F44", 15): (24, "keyword list number (name at col 18)", "measured"),
    ("t0BA6D0", 15): (114, "money line (dyna shop, shop list)", "measured"),
    ("t0BA79C", 15): (112, "shop list spec panel (inner x 233)", "measured"),
    **{(i, 1): (100, "keyword help box (inner x 111; work/qa/help12: a 12-char JP line fits)", "measured")
       for i in ("t0B67A0", "t0B67B8", "t0B67D0", "t0B67E4")},
}

# id ranges by content (work/qa/strmap.txt, phase 5): start, end, px, variant, status
CLASSES = [
    (0x0AF6D0, 0x0AF6DF, 64, "ヨロシク仮面 (where it shows: not found yet)", "guess"),
    (0x0AFCA0, 0x0AFD3C, 32, "sector type names (field build menu header)", "measured"),
    (0x0AFD40, 0x0B211C, 88, "item / device description lines (4-line box) + device names", "measured"),
    (0x0B2128, 0x0B37A0, 64, "Dyna, weapon and device names", "measured"),
    (0x0B37A8, 0x0B3A9C, 64, "attack names", "measured"),
    (0x0B3AA8, 0x0B3DE4, 64, "Dyna types, attributes, kits", "measured"),
    (0x0B3DF4, 0x0B4A68, 64, "item and equipment names, relations", "measured"),
    (0x0B4A70, 0x0B4CA8, 64, "PDA places and events", "guess"),
    (0x0B4CB0, 0x0B5618, 64, "people and Dyna names, styles (name lists; %sRn = 64)", "measured"),
    (0x0B562C, 0x0B802C, 96, "keyword / style names (keyword list: col 18 to the screen edge) and help lines "
     "(help box inner x 111)", "measured"),
    (0x0B8044, 0x0BB7A8, 88, "UI strings (menus, prompts, formats)", "guess"),
]


def placements():
    rows = []
    for ln in MARKS.read_text(encoding="utf-8").splitlines()[1:]:
        f = ln.split("\t")
        if f[0].startswith("t"):
            rows.append((f[0], int(f[1]), int(f[2])))
    return rows


def render():
    per_id = {}
    for sid, size, col in placements():
        w = ID_WINDOW.get((sid, col)) or WINDOW.get((size, col))
        if w is None:
            continue
        if sid not in per_id or w[0] < per_id[sid][0]:
            per_id[sid] = w
    out = ["# start\tend\tpx\tlines\tvariant\tstatus   (generated by tools/budgets.py; first match wins)"]
    for sid in sorted(per_id):
        px, variant, status = per_id[sid]
        off = sid[1:]
        out.append(f"{off}\t{off}\t{px}\t1\t{variant}\t{status}")
    for a, b, px, variant, status in CLASSES:
        out.append(f"{a:06X}\t{b:06X}\t{px}\t1\t{variant}\t{status}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = render()
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("docs/re/budgets.tsv is stale: run tools/budgets.py")
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {text.count(chr(10)) - 1} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
