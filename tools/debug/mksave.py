"""Make work/states/tutorial_jp.sav: the battery save the menu/fscript/dmode warps continue from (warp.lua CONT).

    python -X utf8 tools/debug/mksave.py

On the original ROM (its pages never change, so the recorded tutorial route stays in sync), from an erased flash:
the warp's "menu_saving" scene plays the tutorial, opens system > データセーブ and saves on the city road; the run
holds 400 frames for the write. The game's save is text-independent, so the English build continues from it.
Exit 1 if the warp never arrived or the save came back blank.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
import regen  # noqa: E402


def main():
    out = ROOT / "work" / "qa" / "mksave"
    if out.exists():
        shutil.rmtree(out)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(regen.ROM), "--out", str(out),
           "--sav", str(regen.blank_sav()), "--script", str(ROOT / "tools" / "debug" / "warp.lua"),
           "--var", "SCENE='menu_saving'", "--var", "HOLD=400", "--var", "FINISH=1",
           "--frames", "33000", "--timeout", "1200"]
    subprocess.run(cmd, cwd=ROOT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    sav = out / (regen.ROM.stem + ".sav")
    data = sav.read_bytes() if sav.exists() else b""
    if "HOLD done" not in log or not data.strip(b"\xff"):
        sys.exit(f"mksave: no save made (see {out / 'log.txt'}, {out / 'hold.png'})")
    shutil.copyfile(sav, regen.TUTORIAL_SAV)
    print(f"saved {regen.TUTORIAL_SAV} ({sum(b != 0xFF for b in data)} bytes written)")


if __name__ == "__main__":
    main()
