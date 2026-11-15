"""Write the sibling groups for tools/lua/rotate.lua: one group per pointer table (as cover_tables.py groups them)
that still has an unshown string, holding the build address of every entry and of the unshown ones.

    python -X utf8 tools/debug/rotate.py            # -> work/qa/rotate_probe.lua, prints a summary
    python -X utf8 tools/debug/regen.py SCENE.. --rom build/dynadevice_blue_en.gba --out work/qa/cover/rot \
        --states work/qa/cover/rot/_states --jobs 1 --probe work/qa/rotate_probe.lua

rotate.lua hooks the text renderer 0x080049AC: when a text object's string is an entry of a group with unshown
siblings left, it points the object at the next unshown sibling. The game's own renderer then reads and draws that
string in the same window (same width, same box) as the entry the screen asked for, so table-indexed lists and help
pages are covered from any scene that shows one of their entries. Strings expanded into a RAM buffer first
(registers) are not seen by the hook.
"""
import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import cover  # noqa: E402

OUT = ROOT / "work" / "qa" / "rotate_probe.lua"
PROBE = ROOT / "tools" / "lua" / "rotate.lua"
ROT = ROOT / "work" / "qa" / "cover" / "rot"
SCENES = ROOT / "tools" / "debug" / "scenes.tsv"


def groups(gap=0x10):
    ents = []
    for f in sorted(glob.glob(str(ROOT / "script" / "strings_*.json"))):
        for e in json.load(open(f, encoding="utf-8")):
            if e.get("ptrs"):
                ents.append((min(int(x, 16) for x in e["ptrs"]), e["id"]))
    ents.sort()
    out, cur, last = [], [], None
    for p, i in ents:
        if last is not None and p - last > gap:
            out.append(cur)
            cur = []
        cur.append(i)
        last = p
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=lambda s: int(s, 0), default=0x10)
    ap.add_argument("--run", nargs="*", metavar="SCENE",
                    help="run these scenes one by one (all of scenes.tsv if none named), rewriting the groups before "
                         "each so every run rotates through what is still unshown; logs in work/qa/cover/rot/<scene>")
    ap.add_argument("--redo", action="store_true", help="with --run: rerun scenes that already have a log")
    a = ap.parse_args()
    if a.run is None:
        write(a.gap)
        return
    names = a.run or [ln.split("\t")[0] for ln in SCENES.read_text(encoding="utf-8").splitlines()[1:]
                      if ln.strip() and not ln.startswith("#")]
    for s in names:
        if not a.redo and (ROT / s / "log.txt").exists():
            continue
        if write(a.gap) == 0:
            print("nothing left to rotate")
            return
        r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "regen.py"), s,
                            "--rom", str(cover.BUILD), "--out", str(ROT), "--states", str(ROT / "_states"),
                            "--jobs", "1", "--probe", str(OUT)], capture_output=True, text=True, cwd=ROOT)
        log = ROT / s / "log.txt"
        n = log.read_text(encoding="utf-8", errors="replace").count("\nROT ") if log.exists() else 0
        print(f"{s}: {n} rotated, exit {r.returncode}", flush=True)
    write(a.gap)


def write(gap):
    addr = dict(cover.strings())
    miss = set(cover.unshown(cover.LOGS))
    lines, n_g, n_u = ["ROT_GROUPS = {"], 0, 0
    for g in groups(gap):
        un = [i for i in g if i in miss and i in addr]
        if not un:
            continue
        n_g += 1
        n_u += len(un)
        al = ",".join(f"0x{addr[i]:08X}" for i in g if i in addr)
        ul = ",".join(f"0x{addr[i]:08X}" for i in un)
        lines.append(f"  {{all={{{al}}}, un={{{ul}}}}},  -- {g[0]}")
    lines.append("}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n" + PROBE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {n_g} groups, {n_u} unshown strings", flush=True)
    return n_u


if __name__ == "__main__":
    main()
