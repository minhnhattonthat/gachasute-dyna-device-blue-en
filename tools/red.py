"""red.py: the Dino Device Red build, derived from the Blue English build.

    python -X utf8 tools/red.py        (after tools/build.py; build.py also calls it when the Red dump is present)

Gachasute! Dino Device Red (Japan) is Blue's ROM with 4 bytes changed: the header title "DINODEVICE R" (0xAB), the
game code AAIJ (0xAD), the header checksum (0xBD) and the version flag u32 at 0x080BC41C (1 Blue, 0 Red). The code
branches on that flag (title badge + background, debug menu version string, a few item and table picks); all text,
graphics and code are shared. So the Red English ROM is the Blue English ROM with those 4 bytes taken from Red.
The title screen's Red PATs (archive 0x1FDA / 0x1FDC) are patched with Blue's: tools/gfx.py TITLE_ANIMS.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLUE_JP = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
RED_JP = ROOT / "rom" / "Gachasute! Dino Device Red (Japan).gba"
BLUE_EN = ROOT / "build" / "dynadevice_blue_en.gba"
RED_EN = ROOT / "build" / "dinodevice_red_en.gba"
RED_SHA1 = "9086aa71d23a753cf0e307a37d56c61c3805adb6"
VERSION_BYTES = {0xAB, 0xAD, 0xBD, 0x0BC41C}


def derive(blue_jp, red_jp, blue_en):
    """-> the Red English image. Fails unless Red differs from Blue in exactly VERSION_BYTES and the English
    build left those bytes alone."""
    if hashlib.sha1(red_jp).hexdigest() != RED_SHA1:
        raise ValueError(f"{RED_JP.name}: SHA-1 {hashlib.sha1(red_jp).hexdigest()}, expected {RED_SHA1}")
    if len(blue_jp) != len(red_jp) or len(blue_en) != len(blue_jp):
        raise ValueError("ROM sizes differ")
    diff = {i for i in range(len(blue_jp)) if blue_jp[i] != red_jp[i]}
    if diff != VERSION_BYTES:
        raise ValueError(f"Red differs from Blue at {sorted(map(hex, diff))}, expected {sorted(map(hex, VERSION_BYTES))}")
    touched = [hex(i) for i in VERSION_BYTES if blue_en[i] != blue_jp[i]]
    if touched:
        raise ValueError(f"the English build writes Red/Blue version bytes {touched}")
    out = bytearray(blue_en)
    for i in VERSION_BYTES:
        out[i] = red_jp[i]
    return bytes(out)


def main():
    if not RED_JP.is_file():
        sys.exit(f"missing {RED_JP.relative_to(ROOT)}")
    out = derive(BLUE_JP.read_bytes(), RED_JP.read_bytes(), BLUE_EN.read_bytes())
    RED_EN.write_bytes(out)
    print(f"{RED_EN.relative_to(ROOT)}: {len(out)} bytes, sha1 {hashlib.sha1(out).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
