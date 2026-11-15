"""Release: build, gate everything, make the BPS patch, re-apply and verify it, zip patch + README.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-build]

Stops at the first failure, in this order: build -> tools/check.py (tests + lint) -> smoke boot -> jp_left.py
(--sjis --gba-ptrs, intended runs in tools/jp_known.txt, only runs unchanged from the original) -> qa_gate.py check on
every work/qa/**/manifest.tsv (visual tour and story pass; verdicts in the manifest's sibling `verdicts/`; the visual
tour's recorded ROM, work/qa/tour/tour_build.gba, is replaced by this build first, so the gate fails STALE unless the
tour ran on this build or `qa_gate.py waive` names it) -> textcover.py (log root work/qa, waivers
docs/text_unshown.tsv) -> no unticked line in docs/polish.md -> no template placeholder in README.md -> debug tool off
-> patch -> re-apply to a clean original and compare -> zip. Output: release/Gachasute_Dyna_Device_Blue_EN_v<version>.zip
(patch + README.txt); refuses to overwrite an existing version without --force. Never publishes anything.
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIG = ROOT / "rom/Gachasute! Dyna Device Blue (Japan).gba"
BUILT = ROOT / "build/dynadevice_blue_en.gba"
TOUR_ROM = ROOT / "work/qa/tour/tour_build.gba"
REL = ROOT / "release"
PY = [sys.executable, "-X", "utf8"]


def skill():
    out = subprocess.run([sys.executable, str(ROOT / "tools/skill.py")], capture_output=True, text=True).stdout
    return Path(out.strip().splitlines()[-1]) / "scripts"


def step(name, cmd):
    print(f"== {name}: {' '.join(str(c) for c in cmd)}", flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT)
    if r.returncode:
        sys.exit(f"release stopped: {name} failed (exit {r.returncode})")


def hashes(data):
    return {"size": len(data), "crc32": f"{zlib.crc32(data):08X}", "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest()}


def gates(s):
    manifests = sorted((ROOT / "work/qa").rglob("manifest.tsv"))
    if not manifests:
        sys.exit("release stopped: no work/qa/**/manifest.tsv")
    # the visual tour's gate checks its recorded ROM: make that the build being released
    if TOUR_ROM.exists() and TOUR_ROM.read_bytes() != BUILT.read_bytes():
        print(f"   tour ROM {TOUR_ROM.relative_to(ROOT)} replaced by this build (gate needs a tour or a waiver for it)")
        shutil.copyfile(BUILT, TOUR_ROM)
    for m in manifests:
        step(f"qa_gate {m.relative_to(ROOT)}", PY + [s / "qa_gate.py", "check", m, m.parent / "verdicts"])


def polish():
    open_ = [ln for ln in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
             if ln.startswith("- [ ]")]
    if open_:
        sys.exit("release stopped: docs/polish.md has unticked lines:\n" + "\n".join(open_))
    print("== polish: every line ticked")


def readme():
    t = (ROOT / "README.md").read_text(encoding="utf-8")
    left = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|crc|md5|game|ext|Dialogue|Menus|"
                      r"Title|Name entry|Songs|Translated|none known)[^>]*>", t)
    if left:
        sys.exit(f"release stopped: README.md still has template placeholders: {sorted(set(left))}")
    print("== README: no placeholders")


def debug_off(orig, built):
    """The debug tool is tools/debug/warp.lua, run by the emulator; nothing of it is in the ROM. The release build
    must be the plain build: no marker text, no --qa override, and the leftover debug menu (mode 50) still only
    reachable as in the original (the dispatcher's first pick at 0x08004DD4 unchanged)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import json
    marker = []
    for f in sorted((ROOT / "script").glob("*.json")):
        marker += [e["id"] for e in json.loads(f.read_text(encoding="utf-8"))
                   if re.match(r"^\[[st][0-9A-F]", e.get("en", ""))]
    if marker:
        sys.exit(f"release stopped: marker text in the build source: {marker[:5]}")
    lo, hi = 0x4DB8, 0x4DF0 + 51 * 4  # mode dispatcher + its jump table
    if built[lo:hi] != orig[lo:hi]:
        sys.exit("release stopped: the mode dispatcher differs from the original (debug menu hook left in?)")
    print("== debug tool off: warp is an external Lua script; plain build, mode dispatcher as the original")


README_TXT = """Gachasute! Dyna Device Blue (GBA) - English translation patch v{ver}
=====================================================================

Unofficial English fan translation of Gachasute! Dyna Device Blue (Game Boy Advance, Smilesoft, 2002).
No ROM is included and none will be provided: patch your own dump.

How to patch
------------
1. Get a clean dump of the Japanese game:
     No-Intro: Gachasute! Dyna Device Blue (Japan)
     File size: {o[size]} bytes
     CRC32:  {o[crc32]}
     MD5:    {o[md5]}
     SHA-1:  {o[sha1]}
2. Apply {patch} with any BPS patcher (Floating IPS / flips, Rom Patcher JS at
   https://www.marcrobledo.com/RomPatcher.js/, beat).
3. The patched ROM should have:
     CRC32:  {n[crc32]}
     SHA-1:  {n[sha1]}

Start from a cold boot (no savestates from the Japanese version). Battery saves from the Japanese game should work.
Tested in Mesen 2.2.1 (GBA core) with the official BIOS.

Translation status
------------------
Dialogue and story ............. translated
Menus, items, Dyna, Devices .... translated
PDA apps, help pages ........... translated
Title screen, graphics text .... redrawn in English
Staff roll ..................... redrawn in English
Name entry ..................... English labels; the kana pages stay (names can be typed in kana or Latin)
Postal-code town names ......... left in Japanese (real place-name database)

Known issues: the town names looked up from a postal code (profile / address book) stay in Japanese: they are
a database of real Japanese place names. Some short names are cut to fit 64-pixel slots (e.g. "Flare Ruby"); PDA
timetable subjects are 3-letter abbreviations. Link-cable trading and battles were not tested (one emulator). Please report bugs at
https://github.com/minhnhattonthat/gachasute-dyna-device-blue-en/issues (a savestate helps).

Credits
-------
Translation, hacking and tools: minhnhattonthat, with extensive AI assistance (Claude by Anthropic; review
passes by OpenAI Codex). Corrections are very welcome.
Font: an 8 px variable-width font drawn for this project (MIT).

Gachasute! Dyna Device is (c) 2002 Smilesoft. This is an unofficial fan project, not affiliated with them.
Do not distribute patched ROMs.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    ap.add_argument("--skip-build", action="store_true", help="use the current build/ output (tests still run)")
    a = ap.parse_args()
    name = f"Gachasute_Dyna_Device_Blue_EN_v{a.version}"
    patch, zpath = REL / f"{name}.bps", REL / f"{name}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"{patch.name} / {zpath.name} already exist; pass --force to overwrite")
    s = skill()
    if not a.skip_build:
        step("build", PY + [ROOT / "tools/build.py"])
    step("tests + lint", PY + [ROOT / "tools/check.py"])
    step("smoke", PY + [s / "emu.py", BUILT, "--out", ROOT / "work/qa/release_smoke", "--route",
                        ROOT / "tools/routes/boot.txt", "--smoke"])
    step("jp_left", PY + [s / "jp_left.py", BUILT, "--orig", ORIG, "--sjis", "--gba-ptrs",
                          "--known", ROOT / "tools/jp_known.txt"])
    gates(s)
    step("textcover", PY + [s / "textcover.py", ROOT / "work/qa", ROOT / "build/strings.tsv",
                            "--waive", ROOT / "docs/text_unshown.tsv"])
    polish()
    readme()
    orig, built = ORIG.read_bytes(), BUILT.read_bytes()
    debug_off(orig, built)
    REL.mkdir(exist_ok=True)
    step("patch", PY + [s / "bps.py", "make", ORIG, BUILT, patch])
    check = REL / f"{name}.check.gba"
    step("re-apply", PY + [s / "bps.py", "apply", ORIG, patch, check])
    if check.read_bytes() != built:
        sys.exit("release stopped: re-applied patch differs from the build")
    check.unlink()
    o, n = hashes(orig), hashes(built)
    readme_txt = README_TXT.format(ver=a.version, o=o, n=n, patch=patch.name)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", readme_txt.replace("\n", "\r\n"))
    print(f"== done: {zpath.relative_to(ROOT)} ({zpath.stat().st_size} bytes): {patch.name} "
          f"({patch.stat().st_size} bytes) + README.txt; patched CRC32 {n['crc32']} SHA-1 {n['sha1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
