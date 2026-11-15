"""lint.py: check the English in script/ against the engine's rules and the measured budgets (docs/re/windows.md).

    python -X utf8 tools/lint.py [--warn] [FILE ...]     # exit 1 on any error

Errors (every entry with "en"):
  - the text encodes (vwf.encode_en: glyphs exist, no stray { } [ ] \\);
  - register codes ({%sR4} ...) and {KN} match the Japanese, in order; colour codes too (strings);
  - messages: at most 2 lines per page, each line <= LINE_PX, a page's last line <= LAST_PX (the ▼ arrow), and
    no stub last line (< STUB_CHARS letters under another line, no register in it);
  - strings: each line <= the entry's budget from docs/re/budgets.tsv when it has one.
Warnings (--warn prints them): a string's {KP} count differs from the Japanese (messages are re-paginated
paragraphs, so not for them), a string with no measured budget yet.
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
REG_PX = {"s": 64, "d": 8}                       # %sRn: any name, 8 full-width chars (measured,
                                                 # docs/re/windows.md §String registers); %dRn: per digit (SJIS)
STUB_CHARS = 6                                   # a 2+-line page's last line shorter than this is a widow
REG = re.compile(r"\{%(0?)(\d*)([sdXx])(R\d)?\}")
TAGS = re.compile(r"\{%[^{}]*\}|\{KN\}|\{C\d\}")
# registers known to hold only a few words: (entry id, register) -> those words (counted at the longest one)
REG_WORDS = {
    ("t0BB224", "R0"): ["earth", "thunder", "water", "fire", "none"],   # Dyna Database element (t0B3C0C-t0B3C30)
}


def reg_width(m, entry_id=None):
    kind, digits = m[3], m[2]
    if kind == "s":
        words = REG_WORDS.get((entry_id, m[4]))
        return max(vwf.width(w) for w in words) if words else REG_PX["s"]
    return REG_PX["d"] * (int(digits) if digits else 5)


def line_width(line, entry_id=None):
    px = 0
    pos = 0
    for m in re.finditer(r"\{[^{}]*\}|\[([0-9A-Fa-f]{2})\]", line):
        px += vwf.width(line[pos:m.start()])
        r = REG.fullmatch(m.group())
        if r:
            px += reg_width(r, entry_id)
        elif m[1] is not None:      # [XX] raw byte: an ASCII glyph at its width, half an SJIS cell otherwise
            b = int(m[1], 16)
            px += vwf.char_width(chr(b)) if 0x20 <= b < 0x7F else 0 if b == vwf.PAD else vwf.CELL // 2
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
            a, b, px, lines, variant, *status = ln.split("\t")
            if status and status[0].strip() == "guess":
                variant += " (guess)"
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
    # {%} is the original's typo in s341.00 (docs/re/text.md): it would eat 3 bytes, so the English drops it
    want = [t for t in TAGS.findall(jp) if t != "{%}"]
    if TAGS.findall(en) != want:
        errs.append(f"codes {TAGS.findall(en)} != JP {want}")
    # messages are written as paragraphs and re-paginated by batches.py's wrap, so their page count may differ
    if en.count("{KP}") != jp.count("{KP}") and not e["id"].startswith("s"):
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
            # stub last line: one stray short word under a line (a register counts as a name, so never a stub)
            last = page[-1]
            if len(page) > 1 and "<@" not in en and not REG.search(last) and \
                    0 < len(re.sub(r"\{[^{}]*\}|\[[0-9A-Fa-f]{2}\]", "", last).strip()) < STUB_CHARS:
                errs.append(f"page {pi + 1}: stub last line {last!r} (rewrap: batches.py balances lines)")
    else:
        b = budget_for(e["id"], budgets)
        if b is None:
            warns.append("no measured budget")
        else:
            px, lines, variant = b
            # a window is at least as wide as the JP line the original drew in it (guessed rows, and measured rows
            # whose marker sat in a narrower placement than this text's own, e.g. {%03dR0}／{%03dR1} at 58 px)
            px = max([px] + [line_width(line) for line in jp.split("\n")])
            ls = en.split("\n")
            if len(ls) > lines:
                errs.append(f"{len(ls)} lines > {lines} ({variant})")
            for line in ls:
                w = line_width(line, e["id"])
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
