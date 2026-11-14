"""Try several input routes from one savestate and put their last frames on one contact sheet (exploration helper).

    python -X utf8 tools/debug/probe_routes.py STATE OUTDIR "name=6 b;60 -;6 a;90 -" "name2=..." [--rom ROM]

Each route runs in emu.py from STATE (parallel, 4 at a time); OUTDIR/<name>/final.png is the result and
OUTDIR/sheet.png tiles them in argument order. Used to map the menus and shops for tools/debug/scenes.tsv.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

ROM = "rom/Gachasute! Dyna Device Blue (Japan).gba"


def run(rom, state, out, name, route):
    d = Path(out) / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), rom, "--out", str(d),
           "--state-in", state, "--route-str", route, "--timeout", "300"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return name, r.returncode, d / "final.png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("out")
    ap.add_argument("routes", nargs="+")
    ap.add_argument("--rom", default=ROM)
    a = ap.parse_args()
    jobs = [r.split("=", 1) for r in a.routes]
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda j: run(a.rom, a.state, a.out, j[0], j[1]), jobs))
    for name, code, png in res:
        print(name, "exit", code)
    pngs = [str(p) for _, _, p in res if p.exists()]
    subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), *pngs,
                    "--cols", "4", "--out", str(Path(a.out) / "sheet.png")])


if __name__ == "__main__":
    main()
