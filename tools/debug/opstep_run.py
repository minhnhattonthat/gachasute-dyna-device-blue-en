"""Run warp scenes with tools/lua/opstep.lua beside the warp, to log every script op the game executes.

    python -X utf8 tools/debug/opstep_run.py SCENE.. [--jobs 2] [--hold 4000] [--out work/qa/ops]

Each run mashes A after arrival (MASHA=1) and holds HOLD frames so the scene's scripts play on. Logs land in
<out>/<scene>/log.txt ("OP <op> <pc> <newpc> <ret>" lines); tools/script.py --check-logs reads them.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"


def run(name, out, hold):
    d = out / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(ROM), "--out", str(d),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--script", str(ROOT / "tools" / "lua" / "opstep.lua"),
           "--var", f"SCENE='{name}'", "--var", "MASHA=1", "--var", f"HOLD={hold}",
           "--frames", str(36000 + hold), "--timeout", "1500"]
    subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    log = d / "log.txt"
    n = sum(1 for l in log.read_text(encoding="utf-8", errors="replace").splitlines() if l.startswith("OP ")) if log.exists() else 0
    return name, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--hold", type=int, default=4000)
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "ops"))
    a = ap.parse_args()
    with ThreadPoolExecutor(a.jobs) as ex:
        for name, n in ex.map(lambda s: run(s, Path(a.out), a.hold), a.names):
            print(name, n, flush=True)


if __name__ == "__main__":
    main()
