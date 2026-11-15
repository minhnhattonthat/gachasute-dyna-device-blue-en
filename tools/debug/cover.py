"""Text coverage runs: one hijacked-script run per message script, plus a report of what no run has shown yet.

    python -X utf8 tools/debug/cover.py report [--logs DIR ..]           # unshown ids, by script / string block
    python -X utf8 tools/debug/cover.py scripts [S ..] [--all] [--masha 1|2] [--jobs 4] [--hold 6000] [--idle 300]
    python -X utf8 tools/debug/cover.py waive    # rewrite the auto rows of docs/text_unshown.tsv (data/blank/kept)

`scripts` runs tools/debug/warp.lua kind "script" for each message script that still has an unshown message (or
every one with --all, or the named ones): script 1 at the new game's start becomes script S, A is pressed every 40
frames (MASHA=2: Down then A, the second choice of each Yes/No) and the run stops once no script has run for --idle
frames, or at --hold. Every run starts from one savestate taken just before script 1 starts (work/states/cov_pre.mss,
made on the first call and re-made when the build is newer), so a run is ~15 s instead of a cold boot. Logs go to
work/qa/cover/<masha>/sSSS/log.txt (message drawer + textcover.lua string reads); `report` and textcover.py read them.
"""
import argparse
import queue
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

BUILD = ROOT / "build" / "dynadevice_blue_en.gba"
STRINGS = ROOT / "build" / "strings.tsv"
OUT = ROOT / "work" / "qa" / "cover"
PRE = ROOT / "work" / "states" / "cov_pre.mss"
BLANK = ROOT / "work" / "states" / "blank.sav"
WAIVE = ROOT / "docs" / "text_unshown.tsv"
LOGS = [ROOT / "work" / "qa" / "warp", OUT]
COVER_RANGES = "80AF6D0-80BB7C0,8747DA0-87F0000"   # as tools/debug/regen.py
PRE_FRAMES = 2985    # script 1 starts at f3003 on a cold boot of the English build


def emu(rom, out, scenes, scene, extra, frames):
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{scene}'",
           "--var", f"SCENES='{scenes.as_posix()}'", "--sav", str(BLANK), "--frames", str(frames), "--timeout", "900",
           "--script", str(Path(SKILL) / "scripts" / "lua" / "probes" / "textcover.lua"),
           "--var", f"RANGES='{COVER_RANGES}'", *extra]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT).returncode


def strings():
    rows = []
    for line in STRINGS.read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) >= 2:
            rows.append((f[0], int(f[1], 16)))
    return rows


def shown_addrs(dirs):
    seen = set()
    for d in dirs:
        for log in Path(d).rglob("log.txt"):
            for m in re.finditer(r"^TEXT ([0-9A-Fa-f]+)", log.read_text(encoding="utf-8", errors="replace"), re.M):
                seen.add(int(m.group(1), 16))
    return seen


def waived():
    if not WAIVE.exists():
        return set()
    out = set()
    for line in WAIVE.read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) >= 2 and f[1].strip() and not line.startswith("#"):
            out.add(f[0])
    return out


def unshown(dirs):
    seen, w = shown_addrs(dirs), waived()
    return [i for i, a in strings() if a not in seen and i not in w]


def make_pre(scenes):
    if PRE.exists() and PRE.stat().st_mtime > BUILD.stat().st_mtime:
        return
    d = OUT / "_pre"
    shutil.rmtree(d, ignore_errors=True)
    emu(BUILD, d, scenes, "cov_s001", ["--state-out", str(PRE)], PRE_FRAMES)
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace")
    if "SCRIPT " in log or not PRE.exists():
        sys.exit(f"pre-state: a script started before f{PRE_FRAMES} or no state written ({d / 'log.txt'})")


def cmd_scripts(a):
    OUT.mkdir(parents=True, exist_ok=True)
    if not BLANK.exists():
        BLANK.write_bytes(b"\xff" * 0x10000)
    ids = [i for i, _ in strings() if i.startswith("s")]
    allscripts = sorted({int(i[1:4]) for i in ids})
    if a.names:
        todo = [int(s.lstrip("s")) for s in a.names]
    elif a.all:
        todo = allscripts
    else:
        todo = sorted({int(i[1:4]) for i in unshown(LOGS) if i.startswith("s")})
    scenes = OUT / "scenes.tsv"
    rows = ["name\tkind\targ\thold\tnote"] + [f"cov_s{s:03d}\tscript\t{s}\t{a.hold}\tcover" for s in allscripts + [1]]
    scenes.write_text("\n".join(dict.fromkeys(rows)) + "\n", encoding="utf-8")
    make_pre(scenes)
    slots = queue.Queue()
    rom_dir = OUT / "_roms"
    rom_dir.mkdir(exist_ok=True)
    for j in range(a.jobs):
        p = rom_dir / f"job{j}.gba"
        shutil.copyfile(BUILD, p)
        slots.put(p)
    sub = OUT / f"m{a.masha}"

    def run(s):
        rom = slots.get()
        try:
            d = sub / f"s{s:03d}"
            shutil.rmtree(d, ignore_errors=True)
            code = emu(rom, d, scenes, f"cov_s{s:03d}", ["--state-in", str(PRE), "--var", f"MASHA={a.masha}",
                       "--var", "FINISH=1", "--var", f"IDLEFIN={a.idle}"], a.hold + 200)
        finally:
            slots.put(rom)
        log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
        ok = f"ARRIVED cov_s{s:03d}" in log
        return s, ok, code

    print(f"{len(todo)} scripts, masha {a.masha}, {a.jobs} jobs")
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(run, todo))
    bad = [s for s, ok, _ in res if not ok]
    print(f"{len(res) - len(bad)}/{len(res)} runs reached their script" + (f"; failed: {bad}" if bad else ""))
    cmd_report(a)
    sys.exit(1 if bad else 0)


def cmd_report(a):
    dirs = [Path(d) for d in a.logs] if getattr(a, "logs", None) else LOGS
    rows = strings()
    miss = set(unshown(dirs))
    groups = defaultdict(list)
    for i, _ in rows:
        if i in miss:
            groups[i[:4] if i.startswith("s") else i[:4]].append(i)
    print(f"shown or waived {len(rows) - len(miss)}/{len(rows)}; unshown: "
          f"{sum(1 for i in miss if i.startswith('s'))} messages, {sum(1 for i in miss if not i.startswith('s'))} strings")
    if getattr(a, "verbose", False):
        for g in sorted(groups):
            print(f"{g}\t{len(groups[g])}\t{' '.join(groups[g][:12])}")


AUTO = "# auto"   # rows below this line are rewritten by `cover.py waive`; hand-written rows go above it
DEBUG_MENU = (0x0AF6E0, 0x0AFCA0)   # AGB SYSTEM DEBUG MENU strings (mode 50, docs/re/debug.md), romaji, kept


def auto_reason(e):
    if e["status"] == "data":
        return "not text: the extractor marks it data (graphics or table bytes in the string region)"
    if not e["jp"].strip("　 "):
        return "blank string: nothing to show or translate"
    if e["status"] == "keep" and DEBUG_MENU[0] <= int(e["id"][1:], 16) < DEBUG_MENU[1]:
        return "AGB SYSTEM DEBUG MENU (mode 50): leftover debug menu, no caller in play; romaji kept"
    if e["status"] == "keep":
        return "kept byte-identical: a format, digit or romaji link-debug string with no translated text"
    return None


def cmd_waive(a):
    """Rewrite the auto rows of docs/text_unshown.tsv: data, blank and kept strings no run has shown."""
    import glob
    import json
    head = []
    if WAIVE.exists():
        for line in WAIVE.read_text(encoding="utf-8").splitlines():
            if line.strip() == AUTO:
                break
            head.append(line)
    if not head:
        head = ["# id<TAB>reason: strings accepted as never shown by a coverage run (textcover.py --waive).",
                "# Hand-written rows here; `python -X utf8 tools/debug/cover.py waive` rewrites the block below."]
    manual = {line.split("\t")[0] for line in head if not line.startswith("#")}
    seen = shown_addrs(LOGS)
    addr = dict(strings())
    auto = []
    for f in sorted(glob.glob(str(ROOT / "script" / "strings_*.json"))):
        for e in json.load(open(f, encoding="utf-8")):
            r = auto_reason(e)
            if r and e["id"] not in manual and addr.get(e["id"]) not in seen:
                auto.append(f"{e['id']}\t{r}")
    WAIVE.write_text("\n".join(head + [AUTO] + auto) + "\n", encoding="utf-8")
    print(f"{WAIVE}: {len(manual)} hand-written, {len(auto)} auto rows")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("waive")
    r = sp.add_parser("report")
    r.add_argument("--logs", nargs="*")
    r.add_argument("-v", "--verbose", action="store_true")
    s = sp.add_parser("scripts")
    s.add_argument("names", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--masha", type=int, default=1)
    s.add_argument("--jobs", type=int, default=4)
    s.add_argument("--hold", type=int, default=6000)
    s.add_argument("--idle", type=int, default=300)
    a = ap.parse_args()
    {"report": cmd_report, "scripts": cmd_scripts, "waive": cmd_waive}[a.cmd](a)


if __name__ == "__main__":
    main()
