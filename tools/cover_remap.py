"""cover_remap.py: carry text-coverage logs over to a new build after text-only edits moved strings.

    python -X utf8 tools/cover_remap.py OLD_STRINGS.tsv [--logs work/qa] [--new build/strings.tsv]
                                        [--out work/qa/cover/remap/log.txt]

textcover.py matches "TEXT <hex address>" lines against the build's strings.tsv, so any edit that changes a message's
length moves every later message and voids the old logs. Which string ids the game reaches does not depend on their
English bytes, so an address logged on the old build is mapped old address -> id (OLD_STRINGS.tsv, the strings.tsv of
the build the logs ran on) -> new address (--new), and written as one log for textcover. Only valid when the logs all
ran on the OLD build and the edits since are text-only (no script-flow or pointer-table change). Logs under
cover/remap/ itself and rotation logs kept outside the log root are not read.
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def table(path):
    rows = [ln.split("\t") for ln in Path(path).read_text(encoding="utf-8").splitlines() if "\t" in ln]
    return {r[0]: int(r[1], 16) for r in rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("--logs", default=str(ROOT / "work/qa"))
    ap.add_argument("--new", default=str(ROOT / "build/strings.tsv"))
    ap.add_argument("--out", default=str(ROOT / "work/qa/cover/remap/log.txt"))
    a = ap.parse_args()
    old, new = table(a.old), table(a.new)
    by_addr = {}
    for i, ad in old.items():
        by_addr.setdefault(ad, []).append(i)
    out = Path(a.out).resolve()
    seen, logs = set(), 0
    rx = re.compile(r"TEXT ([0-9A-Fa-f]+)")
    for log in Path(a.logs).rglob("log.txt"):
        if log.resolve().parent == out.parent:
            continue
        logs += 1
        for m in rx.finditer(log.read_text(encoding="utf-8", errors="replace")):
            seen.add(int(m.group(1), 16))
    ids = sorted({i for ad in seen for i in by_addr.get(ad, []) if i in new})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(f"TEXT {new[i]:08X}  {i}\n" for i in ids), encoding="utf-8", newline="\n")
    moved = sum(1 for i in ids if old[i] != new[i])
    print(f"{logs} logs, {len(seen)} addresses, {len(ids)} ids mapped ({moved} moved) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
