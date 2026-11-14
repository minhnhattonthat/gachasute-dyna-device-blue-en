import unittest
from pathlib import Path

import addrdb
import extract
import strtab
from text import decode, encode, tags

ROOT = Path(__file__).resolve().parents[1]
ROMS = list((ROOT / "rom").glob("*.gba"))


class Codec(unittest.TestCase):
    def test_control_codes(self):
        raw = "あKGいKPう%sR4%02dR1C1え".encode("cp932") + b"KN"
        s = decode(raw)
        self.assertEqual(s, "あ\nい{KP}\nう{%sR4}{%02dR1}{C1}え{KN}")
        self.assertEqual(encode(s), raw)
        self.assertEqual(tags(s), ["{KP}", "{%sR4}", "{%02dR1}", "{C1}", "{KN}"])

    def test_kp_without_newline_and_hex_escapes(self):
        self.assertEqual(encode("A{KP}B"), b"AKPB")
        self.assertEqual(decode(b"{\x01"), "[7B][01]")
        self.assertEqual(encode("[7B][01]"), b"{\x01")
        self.assertEqual(decode("%の".encode("cp932")), "{%}の")

    def test_stray_brace_refused(self):
        with self.assertRaises(ValueError):
            encode("oops {KQ}")


@unittest.skipUnless(ROMS, "ROM not present")
class Extraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROMS[0].read_bytes()

    def test_script_json_roundtrips_and_covers_the_text(self):
        # every message and string: encode(decode(raw)) == raw; script/ jp encodes to the ROM bytes; no id missing
        # or extra; no kana run outside the text ranges; no stray byte in the string region
        self.assertEqual(extract.verify(self.rom), [])

    def test_counts(self):
        raws = extract.raw_strings(self.rom)
        self.assertEqual(sum(k.startswith("s") for k in raws), 2824)
        self.assertEqual(sum(k.startswith("t") for k in raws), 2712)

    def test_coverage_scan_sees_missed_text(self):
        rom = bytearray(self.rom)
        rom[0x7F0000:0x7F0008] = "ちがうよ".encode("cp932")  # free space at the ROM end
        self.assertEqual(extract.uncovered_kana(bytes(rom)), [0x7F0000])

    def test_every_string_has_a_pointer(self):
        ps = strtab.pieces(self.rom)
        ptr = strtab.pointers(self.rom, [p[0] for p in ps])
        self.assertEqual([hex(s) for s, v in ptr.items() if not v], [])

    def test_address_db_repacks_identically(self):
        db = addrdb.unpack(self.rom)
        self.assertEqual(len(db["towns"]), 120701)
        self.assertEqual(addrdb.pack(db), self.rom[addrdb.BASE:addrdb.BASE + addrdb.size(self.rom)])


if __name__ == "__main__":
    unittest.main()
