"""marks.py: collect the MARK lines that tools/lua/markerlog.lua logs during a marker tour.

    python -X utf8 tools/marks.py work/qa/p5_mk [--tsv OUT] [--strings] [--group]

Each MARK line: id size col row units. Output: one row per (id, size, col, row) with the scenes that drew it.
--strings keeps the string-table ids only (tOOOOOO). --group prints placements grouped by (size, col): the
window a string lands in, with the id ranges and a JP sample, which is how docs/re/budgets.tsv is laid out.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = re.compile(r"MARK (\S+) size=(\d+) col=(\d+) row=(\d+) units=(\d+)")


def collect(logdir):
    seen = collections.defaultdict(set)   # (id, size, col, row, units) -> scenes
    for log in sorted(Path(logdir).glob("*/log.txt")):
        for ln in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = MARK.search(ln)
            if m:
                i, s, c, r, u = m.groups()
                seen[(i, int(s), int(c), int(r), int(u))].add(log.parent.name)
    return seen


def jp_texts():
    out = {}
    for f in (ROOT / "script").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for e in d["entries"] if isinstance(d, dict) else d:
            out[e["id"]] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logdir")
    ap.add_argument("--tsv")
    ap.add_argument("--strings", action="store_true")
    ap.add_argument("--group", action="store_true")
    a = ap.parse_args()
    seen = collect(a.logdir)
    if a.strings:
        seen = {k: v for k, v in seen.items() if k[0].startswith("t")}
    texts = jp_texts()
    rows = sorted(seen.items())
    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8", newline="\n") as f:
            f.write("id\tsize\tcol\trow\tunits\tscenes\tjp\n")
            for (i, s, c, r, u), sc in rows:
                jp = texts.get(i, {}).get("jp", "").replace("\n", "/")
                f.write(f"{i}\t{s}\t{c}\t{r}\t{u}\t{','.join(sorted(sc))}\t{jp}\n")
    ids = {k[0] for k in seen}
    print(f"{len(rows)} placements, {len(ids)} ids "
          f"({sum(1 for i in ids if i.startswith('t'))} strings, {sum(1 for i in ids if i.startswith('s'))} messages)")
    if a.group:
        g = collections.defaultdict(list)
        for (i, s, c, r, u), sc in rows:
            g[(s, c)].append((i, r, sc))
        for (s, c), items in sorted(g.items()):
            ids_ = sorted({x[0] for x in items})
            rows_ = sorted({x[1] for x in items})
            scenes = sorted(set().union(*(x[2] for x in items)))
            sample = texts.get(ids_[0], {}).get("jp", "").replace("\n", "/")[:24]
            print(f"size={s} col={c:2d} rows={rows_[0]}-{rows_[-1]} n={len(ids_):4d} ids {ids_[0]}..{ids_[-1]} "
                  f"scenes={','.join(scenes[:4])}{'...' if len(scenes) > 4 else ''}  {sample}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
