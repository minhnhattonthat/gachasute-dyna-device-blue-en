"""Regenerate every debug-warp scene from a cold boot: shot + savestate per scene, checked by its log.

    python -X utf8 tools/debug/regen.py [SCENE ...] [--rom ROM] [--jobs 4] [--out work/qa/warp] [--states work/states]
                                        [--probe tools/lua/markerlog.lua]

Runs tools/debug/warp.lua for each scene in tools/debug/scenes.tsv (or the named ones) in parallel. Each run must
log "ARRIVED <scene>" and "HOLD done"; then <out>/<scene>/hold.png is the proof shot and <states>/<scene>.mss the
state. Writes <out>/sheet.png (all hold shots) and exits 1 if any scene failed. Re-run after engine, font or
graphics changes (states carry old code and VRAM).
"""
import argparse
import queue
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
SCENES = ROOT / "tools" / "debug" / "scenes.tsv"
# frame budget per kind: the warp stops itself at the hold shot; this is only the ceiling
BUDGET = {"boot": 4000, "newgame": 5000, "script": 9000, "event": 12000, "field": 12000, "menu": 32000, "fscript": 33000, "mode": 4500,
          "resume": 4500, "dmode": 28000}
# menu, fscript and dmode scenes continue from a save made after the tutorial on the original ROM (warp.lua CONT)
CONT_KINDS = {"menu", "fscript", "dmode"}
CONT_BUDGET = 9000
TUTORIAL_SAV = ROOT / "work" / "states" / "tutorial_jp.sav"
BLANK = ROOT / "work" / "states" / "blank.sav"
COVER_RANGES = "80AF6D0-80BB7C0,8747DA0-87F0000"   # string region, free space (moved strings)


def scenes():
    rows = []
    for line in SCENES.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] != "name":
            rows.append(f)
    return rows


def blank_sav():
    """A fresh erased 64 KB flash: runs that need no save still get their own copy (emu.py --sav), never whatever
    an earlier run left in tools/mesen/Saves/<rom>.sav."""
    if not BLANK.exists():
        BLANK.parent.mkdir(parents=True, exist_ok=True)
        BLANK.write_bytes(b"\xff" * 0x10000)
    return BLANK


def run(rom, out, states, row, probes=(), slots=None):
    name, kind = row[0], row[1]
    hold = int(row[3]) if len(row) > 3 and row[3].strip() else 300
    cont = kind in CONT_KINDS
    saved = cont or (kind == "boot" and row[2].startswith("fortune"))   # the fortune box shows only with a save
    if saved and not TUTORIAL_SAV.exists():
        sys.exit(f"{TUTORIAL_SAV} missing: run tools/debug/mksave.py first")
    d = out / name
    state = states / f"{name}.mss"
    # Mesen keeps one battery file per ROM name: each parallel job runs its own copy of the ROM
    slot = slots.get() if slots else None
    try:
        rom_run = slot or rom
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom_run), "--out", str(d),
               "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{name}'",
               "--var", "FINISH=1", "--var", f"WARP_STATE='{state.as_posix()}'",
               "--sav", str(TUTORIAL_SAV if saved else blank_sav()),
               "--frames", str((CONT_BUDGET if cont else BUDGET.get(kind, 12000)) + hold), "--timeout", "1200"]
        if cont:
            cmd += ["--var", "CONT=1"]
        # text coverage: first-byte reads of strings (region + relocated ones in the free space); messages are
        # logged by warp.lua's TEXT_DRAW hook. textcover.py work/qa/warp build/strings.tsv reads both.
        cmd += ["--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
                "--var", f"RANGES='{COVER_RANGES}'"]
        for p in probes:
            cmd += ["--script", str(Path(p).resolve())]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    finally:
        if slot:
            slots.put(slot)
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    ok = f"ARRIVED {name} " in log and "HOLD done" in log and (d / "hold.png").exists()
    return name, ok, r.returncode, d / "hold.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--rom", default=str(ROM))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "warp"))
    ap.add_argument("--states", default=str(ROOT / "work" / "states"))
    ap.add_argument("--probe", action="append", default=[], help="extra Lua probe run beside warp.lua (repeatable)")
    a = ap.parse_args()
    rows = scenes()
    if a.names:
        known = {r[0] for r in rows}
        bad = [n for n in a.names if n not in known]
        if bad:
            sys.exit(f"unknown scene(s): {' '.join(bad)}")
        rows = [r for r in rows if r[0] in a.names]
    # absolute: the warp saves its state from Mesen, whose working folder is tools/mesen
    out, states = Path(a.out).resolve(), Path(a.states).resolve()
    states.mkdir(parents=True, exist_ok=True)
    # longest first so the menu replays (about 26k frames) don't trail at the end
    rows.sort(key=lambda r: -BUDGET.get(r[1], 12000))
    slots = queue.Queue()
    rom_dir = out / "_roms"
    rom_dir.mkdir(parents=True, exist_ok=True)
    for j in range(a.jobs):
        p = rom_dir / f"job{j}.gba"
        shutil.copyfile(a.rom, p)
        slots.put(p)
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda r: run(a.rom, out, states, r, a.probe, slots), rows))
    # Mesen runs occasionally die under load (8 parallel menu replays: 3 exited 1 mid-route); retry those once
    retry = {n for n, ok, _, _ in res if not ok}
    if retry:
        print(f"retrying {len(retry)}: {' '.join(sorted(retry))}")
        with ThreadPoolExecutor(min(2, a.jobs)) as ex:
            again = {t[0]: t for t in ex.map(lambda r: run(a.rom, out, states, r, a.probe, slots),
                                             [r for r in rows if r[0] in retry])}
        res = [again.get(t[0], t) for t in res]
    order = {r[0]: i for i, r in enumerate(scenes())}
    res.sort(key=lambda t: order[t[0]])
    for name, ok, code, _ in res:
        print(f"{'ok  ' if ok else 'FAIL'} {name} (exit {code})")
    shots = [str(p) for _, ok, _, p in res if ok]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *shots,
                        "--cols", "6", "--out", str(out / "sheet.png")], capture_output=True)
        print(f"sheet: {out / 'sheet.png'}")
    failed = [n for n, ok, _, _ in res if not ok]
    print(f"{len(res) - len(failed)}/{len(res)} scenes reached")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
