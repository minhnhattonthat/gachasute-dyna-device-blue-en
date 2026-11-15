"""Group the non-message strings by the pointer table that reaches them, with how many of each table a coverage run
has shown. Tells which screens (lists, help pages) still need a scene, and which tables are partly shown.

    python -X utf8 tools/debug/cover_tables.py [--gap 0x10] [--min 1] [--unshown]
"""
import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import cover  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=lambda s: int(s, 0), default=0x10)
    ap.add_argument("--unshown", action="store_true", help="only tables with an unshown string")
    a = ap.parse_args()
    miss = set(cover.unshown(cover.LOGS))
    ents = []
    for f in sorted(glob.glob(str(ROOT / "script" / "strings_*.json"))):
        for e in json.load(open(f, encoding="utf-8")):
            p = min(int(x, 16) for x in e["ptrs"]) if e.get("ptrs") else None
            ents.append((p, e))
    ents.sort(key=lambda t: (t[0] is None, t[0] or 0))
    tables, cur, last = [], [], None
    for p, e in ents:
        if p is None or last is None or p - last > a.gap:
            if cur:
                tables.append(cur)
            cur = []
        cur.append((p, e))
        last = p
    if cur:
        tables.append(cur)
    for t in tables:
        n = len(t)
        un = [e for _, e in t if e["id"] in miss]
        if a.unshown and not un:
            continue
        p0 = t[0][0]
        sample = " / ".join((e.get("en") or e["jp"])[:18] for _, e in t[:3])
        print(f"{p0:06X}" if p0 is not None else "noptr ", f"{n - len(un):4d}/{n:<4d}", t[0][1]["id"], sample)


if __name__ == "__main__":
    main()
