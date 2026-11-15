"""romwrite.py: the build's one ROM write function, its write log and the romdiff gate (phase 7).

    log = romwrite.Log(original_rom)
    log.put(out, offset, data, "writer name")       # every build write goes through this
    log.save(path)                                   # build/writes.txt: OFFSET ORIG_HEX NEW_HEX writer
    errors = romwrite.verify(original_rom, out, log) # [] when clean

verify() runs tools/romdiff.py's check with the log (wrong original bytes, overwritten or overlapping writes, a
changed byte no write explains) and also fails on any write outside the allowed ranges: tools/allowed_ranges.txt
plus every pointer word the extractor lists (script/*.json "ptrs").
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import romdiff  # noqa: E402

RANGES = ROOT / "tools" / "allowed_ranges.txt"
SCRIPT_DIR = ROOT / "script"


class Log:
    def __init__(self, orig):
        self.orig = bytes(orig)
        self.rows = []          # (offset, orig bytes, new bytes, writer)

    def put(self, out, off, data, by):
        data = bytes(data)
        if off < 0 or off + len(data) > len(out):
            raise ValueError(f"{by}: write {off:#x}+{len(data)} outside the ROM")
        self.rows.append((off, self.orig[off:off + len(data)].ljust(len(data), b"\xff"), data, by))
        out[off:off + len(data)] = data

    def save(self, path):
        lines = [f"{o:X} {a.hex()} {b.hex()} {by}" for o, a, b, by in sorted(self.rows, key=lambda r: r[0])]
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def put(log, out, off, data, by):
    """Write through `log` when there is one (the build), else directly (unit tests on a scratch buffer)."""
    if log is None:
        out[off:off + len(data)] = data
    else:
        log.put(out, off, data, by)


def allowed_ranges(path=RANGES, script_dir=SCRIPT_DIR):
    """-> sorted list of (start, end) inclusive: the ranges file plus every 4-byte pointer word in script/."""
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.split("#")[0].strip()
        if not ln:
            continue
        lo, _, hi = ln.split()[0].partition("-")
        out.append((int(lo, 16), int(hi or lo, 16)))
    for f in sorted(Path(script_dir).glob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            for p in e.get("ptrs", []):
                p = int(p, 16)
                out.append((p, p + 3))
    return sorted(out)


def outside(rows, ranges):
    """-> error lines for every write (or part of one) not inside an allowed range."""
    errs = []
    for off, a, _, by in rows:
        end = off + len(a) - 1
        # ranges are sorted; merge the ones touching [off, end] and see whether they cover it
        pos = off
        for lo, hi in ranges:
            if hi < pos:
                continue
            if lo > pos:
                break
            pos = hi + 1
            if pos > end:
                break
        if pos <= end:
            errs.append(f"0x{off:06X}: {by} writes {len(a)} bytes, 0x{pos:06X} is outside the allowed ranges")
    return errs


def verify(orig, new, log, ranges=None):
    ranges = allowed_ranges() if ranges is None else ranges
    errs, _ = romdiff.check(bytes(orig), bytes(new), set(), log.rows)
    return errs + outside(log.rows, ranges)
