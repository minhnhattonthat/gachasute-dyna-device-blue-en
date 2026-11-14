"""addrdb.py: the address database (resource file 2, ROM 0x44C754-0x702BB4): Japanese postal codes with their
prefecture, municipality and town names. Parse and repack, byte-exact.

    python -X utf8 tools/addrdb.py            # counts + identity repack check

Layout (docs/re/text.md), all names Shift-JIS, NUL-padded to a fixed width:
  header  4 x u32 LE offsets from the file start: towns (0x10), prefectures, municipalities, end (= file size)
  towns   120701 records of 23 bytes: u32 BE postal code (7 digits), u8 prefecture index, u16 BE municipality
          index, 16-byte town name (empty = the code's catch-all entry); then 5 zero bytes
  prefs   48 x 10 bytes
  cities  3356 x 20 bytes
The file ends with "end\\x1a" + 12 zero bytes like the other resource files (outside the parsed size).
Translation plan (non-blocking question in docs/status.md): Hepburn from Japan Post KEN_ALL readings by postal code.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
BASE = 0x44C754
TOWN_LEN, TOWN_NAME = 23, 16
PREF_LEN, CITY_LEN = 10, 20


def unpack(rom, base=BASE):
    """-> dict(towns=[(postal, pref, city, name bytes)], prefs=[bytes], cities=[bytes], tail=bytes)."""
    t, p, c, end = struct.unpack_from("<4I", rom, base)
    n = (p - t) // TOWN_LEN
    towns = []
    for k in range(n):
        a = base + t + k * TOWN_LEN
        postal, pref, city = struct.unpack_from(">IBH", rom, a)
        towns.append((postal, pref, city, rom[a + 7:a + TOWN_LEN].rstrip(b"\0")))
    tail = rom[base + t + n * TOWN_LEN:base + p]
    prefs = [rom[base + p + k:base + p + k + PREF_LEN].rstrip(b"\0") for k in range(0, c - p, PREF_LEN)]
    cities = [rom[base + c + k:base + c + k + CITY_LEN].rstrip(b"\0") for k in range(0, end - c, CITY_LEN)]
    return dict(towns=towns, prefs=prefs, cities=cities, tail=tail)


def _field(name, width):
    if len(name) > width:
        raise ValueError(f"name {name!r} longer than {width} bytes")
    return name + bytes(width - len(name))


def pack(db):
    """-> the file bytes covered by the header (no end marker)."""
    towns = b"".join(struct.pack(">IBH", po, pr, ci) + _field(nm, TOWN_NAME) for po, pr, ci, nm in db["towns"])
    towns += db["tail"]
    prefs = b"".join(_field(x, PREF_LEN) for x in db["prefs"])
    cities = b"".join(_field(x, CITY_LEN) for x in db["cities"])
    t = 0x10
    p = t + len(towns)
    c = p + len(prefs)
    end = c + len(cities)
    return struct.pack("<4I", t, p, c, end) + towns + prefs + cities


def size(rom, base=BASE):
    return struct.unpack_from("<4I", rom, base)[3]


def main():
    rom = ROM.read_bytes()
    db = unpack(rom)
    same = pack(db) == rom[BASE:BASE + size(rom)]
    names = {x[3] for x in db["towns"]}
    print(f"{len(db['towns'])} towns ({len(names)} distinct names), {len(db['prefs'])} prefectures, "
          f"{len(db['cities'])} municipalities; repack {'identical' if same else 'DIFFERENT'}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
