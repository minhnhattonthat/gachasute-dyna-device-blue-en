"""postal_check.py: type postal codes on the profile form of a build and compare the address the game's lookup
writes (tools/lua/addrprobe.lua SETFIELD) with tools/addrdb.py's model. Exit 1 on any difference.

    python -X utf8 tools/debug/postal_check.py [--rom build/dynadevice_blue_en.gba] 1000005 4070033 ...
Shots: work/qa/addr/<code>/hold.png (the form with the address).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
import addrdb  # noqa: E402
import postal_route  # noqa: E402
import skill  # noqa: E402


def expected(code):
    rom = addrdb.ROM.read_bytes()
    db = addrdb.unpack(rom)
    p, c, t = addrdb.load_en()
    for po, pr, ci, nm in db["towns"]:
        if po == code:
            town = t.get((pr, ci, nm), "") if nm else ""
            return addrdb.choose(p[pr], c[ci], town)[1]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="+")
    ap.add_argument("--rom", default=str(ROOT / "build" / "dynadevice_blue_en.gba"))
    a = ap.parse_args()
    emu = Path(skill.SKILL) / "scripts" / "emu.py"
    bad = 0
    for code in a.codes:
        out = ROOT / "work" / "qa" / "addr" / code
        out.mkdir(parents=True, exist_ok=True)
        scenes = out / "scene.tsv"
        scenes.write_text(f"pc\tboot\tform|{postal_route.route(code)}\t1200\tx\n", encoding="utf8")
        subprocess.run([sys.executable, "-X", "utf8", str(emu), a.rom, "--out", str(out),
                        "--script", str(ROOT / "tools/debug/warp.lua"), "--script", str(ROOT / "tools/lua/addrprobe.lua"),
                        "--var", "SCENE='pc'", "--var", f"SCENES='{scenes.as_posix()}'", "--var", "FINISH=1",
                        "--frames", "4000"], check=True, capture_output=True)
        log = (out / "log.txt").read_text(encoding="utf8", errors="replace")
        m = re.search(r"SETFIELD f=\d+ text=([0-9A-F]+)", log)
        got = bytes.fromhex(m.group(1)).split(b"\0")[0] if m else None
        want = expected(int(code))
        ok = got == want
        bad += not ok
        print(f"{code}  {'ok  ' if ok else 'DIFF'}  game={got!r}" + ("" if ok else f"\n               model={want!r}"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
