"""extract.py: dump the game text to script/ JSON and verify it against the ROM.

    python -X utf8 tools/extract.py dump [--force]   # writes missing files; --force refreshes jp/meta, keeps en
    python -X utf8 tools/extract.py verify           # roundtrip + coverage (tests/test_extract.py runs the same)

Files (indent=1, ensure_ascii=False), one entry per string:
  script/events_NNN.json   event-script messages, scripts NNN..NNN+49 (tools/script.py). Entry:
      id "sSSS.KK" (script, message index in it), flag, speaker (-1 = none), jp, en, status
  script/strings_XXX.json  NUL-terminated strings at 0xXXX000-0xXXXFFF of the string region (tools/strtab.py):
      id "tOOOOOO" (ROM offset), ptrs (ROM offsets of the u32 words pointing at it), slot (bytes free in place,
      incl. the NUL and padding), jp, en, status
status: "todo"; "keep" = stays as is (debug menu, ASCII formats); "data" = not text for translation (the
name-entry keyboard layout, reworked with the font in phase 5). The address database (tools/addrdb.py) is
romanized by a tool, not dumped here. Text form: tools/text.py.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import addrdb  # noqa: E402
import script  # noqa: E402
import strtab  # noqa: E402
from text import decode, encode  # noqa: E402

OUT = ROOT / "script"
EVENTS_PER_FILE = 50
# Kana runs outside the text ranges that are not text: tile-map bytes (0x3BE7xx-0x3BEDxx) and graphics noise.
NOT_TEXT = [(0x3BE700, 0x3BED60), (0x3D97B0, 0x3D97C0)]
KANA_RUN = re.compile(rb"(?:\x82[\x9f-\xf1]|\x83[\x40-\x96]|\x81[\x5b\x40]){3,}")
KEYBOARD = re.compile(rb"^(?:tb|so|ED)|(?:tb|so|ED)$")
GRID = (0x0D21F0, 0x0D22F8)  # pointer table of the name-entry keyboard pages (one row string per entry)


def event_entries(rom):
    """-> {file name: [entries]} for the 2824 messages."""
    files = {}
    for i, ops in enumerate(script.unpack(rom)):
        msgs = [op for op in ops if op.code == script.MSG]
        name = f"events_{i - i % EVENTS_PER_FILE:03d}.json"
        lst = files.setdefault(name, [])
        for k, op in enumerate(msgs):
            lst.append({"id": f"s{i:03d}.{k:02d}", "flag": op.flag, "speaker": op.speaker,
                        "jp": decode(op.text), "en": "", "status": "todo"})
    return files


def string_status(start, raw, ptrs):
    if strtab.DEBUG[0] <= start < strtab.DEBUG[1]:
        return "keep", "AGB debug menu (romaji, debug build only)"
    if KEYBOARD.search(raw):
        return "data", "name-entry keyboard layout (tb = row, so = key, ED = end)"
    if ptrs and all(GRID[0] <= a < GRID[1] for a in ptrs):
        return "data", "name-entry keyboard grid row (pointer table 0x0D21F0)"
    if all(b < 0x80 for b in raw):
        return "keep", "ASCII: number format or debug label"
    return "todo", None


def string_entries(rom):
    ps = strtab.pieces(rom)
    ptr = strtab.pointers(rom, [p[0] for p in ps])
    files = {}
    for start, raw, slot in ps:
        status, note = string_status(start, raw, ptr[start])
        e = {"id": f"t{start:06X}", "ptrs": [f"{a:06X}" for a in ptr[start]], "slot": slot,
             "jp": decode(raw), "en": "", "status": status}
        if note:
            e["notes"] = note
        files.setdefault(f"strings_{start >> 12:03X}.json", []).append(e)
    return files


def all_entries(rom):
    files = event_entries(rom)
    files.update(string_entries(rom))
    return files


def write(path, entries):
    path.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def dump(rom, force=False):
    OUT.mkdir(exist_ok=True)
    for name, entries in all_entries(rom).items():
        path = OUT / name
        if path.exists() and not force:
            print(f"kept {name} (exists; --force refreshes jp and keeps en)")
            continue
        if path.exists():
            old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
            for e in entries:
                o = old.get(e["id"])
                if not o or not o.get("en"):
                    continue  # nothing translated: take the fresh status and notes
                if o["jp"] != e["jp"] and o.get("en"):
                    print(f"  {e['id']}: jp changed under an existing translation; status set to retranslate")
                    o["status"] = "retranslate"
                for k in ("en", "status", "notes"):
                    if k in o:
                        e[k] = o[k]
        write(path, entries)
        print(f"wrote {name} ({len(entries)})")


def load():
    """-> {id: entry} over every script/*.json."""
    out = {}
    for path in sorted(OUT.glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            if e["id"] in out:
                raise ValueError(f"duplicate id {e['id']} in {path.name}")
            out[e["id"]] = e
    return out


def raw_strings(rom):
    """-> {id: original bytes} for every string the extractor covers."""
    out = {}
    for i, ops in enumerate(script.unpack(rom)):
        for k, op in enumerate(op for op in ops if op.code == script.MSG):
            out[f"s{i:03d}.{k:02d}"] = op.text
    for start, raw, _slot in strtab.pieces(rom):
        out[f"t{start:06X}"] = raw
    return out


def uncovered_kana(rom):
    """Kana runs (3+) outside the extracted ranges and the known non-text spots: text the extractor misses."""
    known = [(strtab.LO, strtab.HI), (script.BASE, script.END),
             (addrdb.BASE, addrdb.BASE + addrdb.size(rom))] + NOT_TEXT
    return [m.start() for m in KANA_RUN.finditer(rom) if not any(lo <= m.start() < hi for lo, hi in known)]


def region_gaps(rom):
    """Non-zero bytes in the string region outside every extracted string (must be none)."""
    covered = bytearray(strtab.HI - strtab.LO)
    for start, raw, _slot in strtab.pieces(rom):
        covered[start - strtab.LO:start - strtab.LO + len(raw) + 1] = b"\1" * (len(raw) + 1)
    return [strtab.LO + k for k in range(len(covered)) if not covered[k] and rom[strtab.LO + k]]


def verify(rom):
    """-> list of problems: JSON vs ROM, codec roundtrip, coverage."""
    problems = []
    raws = raw_strings(rom)
    for sid, raw in raws.items():
        if encode(decode(raw)) != raw:
            problems.append(f"{sid}: codec roundtrip differs")
    try:
        js = load()
    except (OSError, ValueError) as ex:
        return problems + [f"script/: {ex}"]
    for sid in raws.keys() - js.keys():
        problems.append(f"{sid}: missing from script/")
    for sid in js.keys() - raws.keys():
        problems.append(f"{sid}: in script/ but not in the ROM")
    for sid in raws.keys() & js.keys():
        if encode(js[sid]["jp"]) != raws[sid]:
            problems.append(f"{sid}: jp in script/ does not encode to the ROM bytes")
    problems += [f"kana at {a:06X} outside every text range" for a in uncovered_kana(rom)]
    problems += [f"string region byte {a:06X} outside every string" for a in region_gaps(rom)[:20]]
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump", "verify"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    rom = script.ROM.read_bytes()
    if a.cmd == "dump":
        dump(rom, a.force)
        return 0
    problems = verify(rom)
    js = load()
    by = {}
    for e in js.values():
        by[e["status"]] = by.get(e["status"], 0) + 1
    print(f"{len(js)} entries {by}; {len(problems)} problems")
    for p in problems[:40]:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
