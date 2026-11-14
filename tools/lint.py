"""lint.py: check the English in script/ against the engine's rules and the measured budgets (docs/re/windows.md).

    python -X utf8 tools/lint.py [--warn] [FILE ...]     # exit 1 on any error

Errors (every entry with "en"):
  - the text encodes (vwf.encode_en: glyphs exist, no stray { } [ ] \\);
  - register codes ({%sR4} ...) and {KN} match the Japanese, in order; colour codes too (strings);
  - messages: at most 2 lines per page, each line <= LINE_PX, a page's last line <= LAST_PX (the ▼ arrow);
  - strings: each line <= the entry's budget from docs/re/budgets.tsv when it has one.
Warnings (--warn prints them): {KP} count differs from the Japanese (extra pages are fine, but check), a string
with no measured budget yet.
A register code counts as REG_PX[kind] pixels (names: the longest English name the register can hold).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vwf  # noqa: E402

SCRIPT = ROOT / "script"
BUDGETS = ROOT / "docs" / "re" / "budgets.tsv"
LINE_PX, LAST_PX, PAGE_LINES = 188, 176, 2      # message box, measured (docs/re/windows.md)
REG_PX = {"s": 64, "d": 8}                       # %sRn: a name (guess until measured); %dRn: per digit (SJIS)
REG = re.compile(r"\{%(0?)(\d*)([sdXx])(R\d)?\}")
TAGS = re.compile(r"\{%[^{}]*\}|\{KN\}|\{C\d\}")


def reg_width(m):
    kind, digits = m[3], m[2]
    if kind == "s":
        return REG_PX["s"]
    return REG_PX["d"] * (int(digits) if digits else 5)


def line_width(line):
    px = 0
    pos = 0
    for m in re.finditer(r"\{[^{}]*\}", line):
        px += vwf.width(line[pos:m.start()])
        r = REG.fullmatch(m.group())
        if r:
            px += reg_width(r)
        pos = m.end()
    return px + vwf.width(line[pos:])


def pages(text):
    """-> list of pages, each a list of lines (codes other than KP/newline kept in the line)."""
    return [p.split("\n") for p in re.split(r"\{KP\}\n?", text)]


def load_budgets():
    """budgets.tsv: id-range start, end (hex, inclusive), px, lines, variant. -> list of tuples."""
    out = []
    if BUDGETS.exists():
        for ln in BUDGETS.read_text(encoding="utf-8").splitlines():
            if not ln.strip() or ln.startswith("#"):
                continue
            a, b, px, lines, variant = ln.split("\t")[:5]
            out.append((int(a, 16), int(b, 16), int(px), int(lines), variant))
    return out


def budget_for(entry_id, budgets):
    off = int(entry_id[1:], 16)
    for a, b, px, lines, variant in budgets:
        if a <= off <= b:
            return px, lines, variant
    return None


def check_entry(e, budgets):
    errs, warns = [], []
    en, jp = e.get("en", ""), e["jp"]
    if not en:
        return errs, warns
    try:
        vwf.encode_en(en)
    except ValueError as x:
        errs.append(str(x))
        return errs, warns
    if TAGS.findall(en) != TAGS.findall(jp):
        errs.append(f"codes {TAGS.findall(en)} != JP {TAGS.findall(jp)}")
    if en.count("{KP}") != jp.count("{KP}"):
        warns.append(f"{{KP}} x{en.count('{KP}')} vs JP x{jp.count('{KP}')}")
    if e["id"].startswith("s"):
        for pi, page in enumerate(pages(en)):
            if len(page) > PAGE_LINES:
                errs.append(f"page {pi + 1}: {len(page)} lines (max {PAGE_LINES})")
            for li, line in enumerate(page):
                lim = LAST_PX if li == len(page) - 1 else LINE_PX
                w = line_width(line)
                if w > lim:
                    errs.append(f"page {pi + 1} line {li + 1}: {w} px > {lim}: {line!r}")
    else:
        b = budget_for(e["id"], budgets)
        if b is None:
            warns.append("no measured budget")
        else:
            px, lines, variant = b
            ls = en.split("\n")
            if len(ls) > lines:
                errs.append(f"{len(ls)} lines > {lines} ({variant})")
            for line in ls:
                w = line_width(line)
                if w > px:
                    errs.append(f"{w} px > {px} ({variant}): {line!r}")
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--warn", action="store_true")
    a = ap.parse_args()
    files = [Path(f) for f in a.files] or sorted(SCRIPT.glob("*.json"))
    budgets = load_budgets()
    nerr = nwarn = 0
    for f in files:
        for e in json.loads(f.read_text(encoding="utf-8")):
            errs, warns = check_entry(e, budgets)
            for x in errs:
                print(f"ERROR {f.name} {e['id']}: {x}")
            nerr += len(errs)
            nwarn += len(warns)
            if a.warn:
                for x in warns:
                    print(f"warn  {f.name} {e['id']}: {x}")
    print(f"lint: {nerr} errors, {nwarn} warnings")
    return 1 if nerr else 0


if __name__ == "__main__":
    sys.exit(main())
