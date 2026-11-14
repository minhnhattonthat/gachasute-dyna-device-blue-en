"""desc_view.py: show the 4-line description records that use a batch's string fragments.

Usage: python -X utf8 tools/desc_view.py bNNN [--dump]

Item/device descriptions (0x0AFD40-0x0B211C) are shared line fragments; a record at 0x0BDB2C + 16k holds 4 line
pointers read as one JP phrase. For each distinct record touching the batch this prints the 4 lines, translated
fragments as «English». --dump rewrites work/tl/desc_records.txt from the ROM first. Read-only on script/.
"""
import glob
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REC_START, REC_END = 0x0BDB2C, 0x0BFAEC
DUMP = ROOT / "work" / "tl" / "desc_records.txt"


def dump():
    rom = Path(glob.glob(str(ROOT / "rom" / "*.gba"))[0]).read_bytes()

    def s(q):
        return rom[q:rom.index(b"\0", q)].decode("cp932", "replace")

    out = ["# description records 0x0BDB2C-0x0BFAEC (4 line pointers each, read as one phrase in JP order)"]
    for o in range(REC_START, REC_END, 16):
        ps = [struct.unpack_from("<I", rom, o + 4 * k)[0] - 0x8000000 for k in range(4)]
        out.append(f"{o:06X}\t" + "\t".join(f"t{p:06X}={s(p)}" for p in ps))
    DUMP.write_text("\n".join(out) + "\n", encoding="utf8")


def main():
    args = sys.argv[1:]
    if "--dump" in args or not DUMP.exists():
        dump()
    batch = next(a for a in args if not a.startswith("--"))
    en = {}
    for f in (ROOT / "script").glob("strings_*.json"):
        for e in json.loads(f.read_text(encoding="utf8")):
            en[e["id"]] = e.get("en") or ""
    ids = {line.split("\t")[0] for line in (ROOT / "work" / "tl" / f"{batch}.tsv").read_text(encoding="utf8").splitlines()}
    seen = set()
    for line in DUMP.read_text(encoding="utf8").splitlines():
        if line.startswith("#"):
            continue
        parts = line.split("\t")[1:]
        pids = tuple(p.split("=", 1)[0] for p in parts)
        if pids in seen or not ids & set(pids):
            continue
        seen.add(pids)
        cells = [f"«{en[i]}»" if en.get(i) else (f"[{i}]" + p.split("=", 1)[1]) for i, p in zip(pids, parts)]
        print(" / ".join(cells))


if __name__ == "__main__":
    main()
