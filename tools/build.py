"""build.py: build build/dynadevice_blue_en.gba from the dump listed in rom.sha1.

    python -X utf8 tools/build.py [--out build/dynadevice_blue_en.gba] [--marker] [--identity] [--qa sSSS.KK=TEXT]

Default: the English build: the VWF renderer (tools/vwf.py) plus every script/ entry with "en" (tools/insert.py).
--marker: every todo entry becomes "[id] filler" (phase 5). --identity: unpack and repack only, byte-identical to
the original (tests/test_script.py). Prints the output's SHA-1 and whether it equals the original.
Every write goes through tools/romwrite.py: the log lands next to the output (<name>.writes.txt) and the build
fails (writing nothing) on any romdiff problem or a write outside tools/allowed_ranges.txt + the pointer words.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import addrdb  # noqa: E402
import check_rom  # noqa: E402
import gfx  # noqa: E402
import insert  # noqa: E402
import romwrite  # noqa: E402
import script  # noqa: E402
import strings_tsv  # noqa: E402
import vwf  # noqa: E402

ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
OUT = ROOT / "build" / "dynadevice_blue_en.gba"
# Zero-filled free space at the end of the 8 MiB ROM (0x747D94..0x800000, docs/re/text.md); 16-aligned start.
FREE_START, FREE_END = 0x747DA0, 0x800000


def place_script_file(out, blob, log=None):
    """Write the packed script file in its original slot if it fits, else at FREE_START, and point the resource
    directory at it. Returns the ROM offset used."""
    if len(blob) <= script.END - script.BASE:
        at = script.BASE
        romwrite.put(log, out, at, blob + bytes(script.END - script.BASE - len(blob)), "script file")
    else:
        at = FREE_START
        if at + len(blob) > FREE_END:
            raise ValueError(f"script file of {len(blob)} bytes does not fit in the free space")
        romwrite.put(log, out, at, blob, "script file (moved)")
    romwrite.put(log, out, script.DIR_WORD, (0x08000000 + at).to_bytes(4, "little"), "script file directory word")
    return at


def build(rom, scripts=None, english=False, entries=None, marker=False, report=None, log=None):
    """-> the built ROM image (bytearray). scripts: 834 op lists (script.unpack); None = the original ones.
    english: install the VWF renderer (tools/vwf.py) and the string-region entries (tools/insert.py) from
    `entries` (None = none changed). log: a romwrite.Log that records every write (romwrite.verify)."""
    out = bytearray(rom)
    if scripts is None:
        scripts = script.unpack(rom)
    blob = script.pack(scripts)
    at = place_script_file(out, blob, log)
    if english:
        free = FREE_START if at != FREE_START else (FREE_START + len(blob) + 15) & ~15
        if entries:
            free, inplace, moved = insert.place_strings(out, entries, marker, free, vwf.VWF_AT, log)
            if report is not None:
                report.update(strings_in_place=inplace, strings_moved=moved, free_used_to=free)
        free = gfx.apply(rom, out, free, log, limit=vwf.VWF_AT)
        if report is not None:
            report["free_used_to"] = free
        vwf.apply(out, log)
        addrdb.apply_en(rom, out, log)
    return out


def stress_scripts(rom):
    """Every message gets "＊" (SJIS 81 96) appended, so the file outgrows its slot: an in-game check of the jump
    fix-ups and the relocation (build.py --stress, then warp scenes on it)."""
    scripts = script.unpack(rom)
    for ops in scripts:
        for op in ops:
            if op.code == script.MSG and len(op.text) % 2 == 0:
                op.text += "＊".encode("cp932")
    return scripts


def qa_override(scripts, spec):
    """--qa sSSS.KK=TEXT: replace one message's text (tools/text.py form, a typed \\n = newline; an odd length gets
    a trailing space)."""
    mid, _, txt = spec.partition("=")
    mid, _, speaker = mid.partition("@")  # sSSS.KK@-1 also sets the speaker (-1 = no portrait)
    txt = txt.replace("\\n", "\n")  # a shell-typed \n is a line break
    s, k = int(mid[1:4]), int(mid[5:7])
    op = [op for op in scripts[s] if op.code == script.MSG][k]
    op.text = vwf.encode_en(txt)
    if speaker:
        op.speaker = int(speaker)


def wide_ids(tsv, px):
    """-> {id: px} for every size-3 row of a marks TSV (an id seen at size 1 anywhere stays at the JP width)."""
    rows = [ln.split("\t") for ln in Path(tsv).read_text(encoding="utf-8").splitlines()[1:] if ln.strip()]
    small = {r[0] for r in rows if len(r) > 1 and r[1] == "1"}
    return {r[0]: px for r in rows if r[0].startswith("t") and r[0] not in small}


def qa_string(entries, spec):
    """--qa tOOOOOO=TEXT: give one string-region entry this English (text.py form) for the build."""
    sid, _, txt = spec.partition("=")
    if sid not in entries:
        raise SystemExit(f"--qa: no string {sid}")
    entries[sid] = dict(entries[sid], en=txt.replace("\\n", "\n"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--stress", action="store_true", help="append ＊ to every message (relocation test build)")
    ap.add_argument("--qa", action="append", default=[], metavar="sSSS.KK=TEXT",
                    help="engine test: replace one message's text, or a string's (tOOOOOO=TEXT) (repeatable)")
    ap.add_argument("--identity", action="store_true", help="no VWF, no text changes: must equal the original")
    ap.add_argument("--marker", action="store_true", help="every todo line -> [id] + filler (phase 5 marker build)")
    ap.add_argument("--marker-px", type=int, default=0,
                    help="with --marker: fill every string marker line to N px (width gate) instead of the JP width")
    ap.add_argument("--marker-ids", metavar="TSV",
                    help="with --marker-px: widen only the ids in this file's first column (tools/marks.py --tsv; "
                         "an optional 'size' column keeps size-1 rows at the JP width)")
    a = ap.parse_args()
    if a.marker and a.marker_px:
        a.marker = a.marker_px
        if a.marker_ids:
            a.marker = wide_ids(a.marker_ids, a.marker_px)
    check_rom.check()
    rom = ROM.read_bytes()
    entries = None
    if a.stress:
        scripts = stress_scripts(rom)
    elif a.identity:
        scripts = script.unpack(rom)
    else:
        entries = insert.load_entries()
        scripts = insert.message_scripts(rom, entries, marker=a.marker)
    for spec in a.qa:
        if spec.startswith("t"):
            if entries is None:
                raise SystemExit("--qa tOOOOOO needs an English or marker build")
            qa_string(entries, spec)
        else:
            qa_override(scripts, spec)
    report = {}
    log = romwrite.Log(rom)
    out = build(rom, scripts, english=not a.identity, entries=entries, marker=a.marker, report=report, log=log)
    if report:
        print(f"strings: {report['strings_in_place']} in place, {report['strings_moved']} moved; free space used to "
              f"{report['free_used_to']:#x} (VWF at {vwf.VWF_AT:#x})")
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    writes = path.with_name(path.stem + ".writes.txt")
    log.save(writes)
    errs = romwrite.verify(rom, out, log)
    for e in errs[:40]:
        print("romdiff:", e)
    if errs:
        raise SystemExit(f"romdiff: {len(errs)} problems (write log {writes}); nothing written to {path}")
    print(f"romdiff: {len(log.rows)} writes, all inside tools/allowed_ranges.txt + pointer words, no stray bytes")
    path.write_bytes(out)
    if not a.identity and not a.marker and path.resolve() == OUT.resolve():
        n = strings_tsv.write(bytes(out))   # build/strings.tsv: text coverage ids + addresses
        print(f"build/strings.tsv: {n} ids")
    sha = hashlib.sha1(out).hexdigest()
    print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {len(out)} bytes, sha1 {sha}"
          f"{' (identical to the original)' if out == rom else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
