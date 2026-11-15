"""The English address database (tools/addrdb.py, tools/addr_en.py, script/addr_*.tsv; docs/re/text.md)."""
import json
import struct
import unittest
from pathlib import Path

import addrdb

ROOT = Path(__file__).resolve().parents[1]


class Layout(unittest.TestCase):
    def check(self, text):
        self.assertLessEqual(len(text), addrdb.MAX_LEN)
        self.assertEqual(len(text) % 2, 0)               # the player's SJIS stays on even bytes
        self.assertTrue(all(0x20 <= b <= 0x7F for b in text))

    def test_fits_one_piece(self):
        text, cut = addrdb.built_text("Tokyo", "Chiyoda-ku", "Marunouchi")
        self.assertEqual(text, b"Tokyo Chiyoda-kuMarunouchi")    # 16 + 10: both pieces of row 1
        self.assertFalse(cut)

    def test_word_moves_to_the_next_piece(self):
        text, cut = addrdb.built_text("Hokkaido", "Sapporo Chuo-ku", "Kita 1-jonishi")
        self.assertEqual(text, b"Hokkaido SapporoChuo-ku\x7f\x7f\x7fKita 1-jonishi \x7f")
        self.assertFalse(cut)
        self.check(text)

    def test_word_skips_a_piece_too_small(self):
        # 12 letters never fit a 10-byte piece: it pads on to the next 16-byte one
        text, _ = addrdb.built_text("", "Sapporo", "Higashinaebo")
        self.assertEqual(text[:7], b"Sapporo")
        self.assertEqual(text[26:38], b"Higashinaebo")
        self.check(text)

    def test_overlong_is_cut_at_the_limit(self):
        text, cut = addrdb.built_text("Yamanashi", "Nirasaki-shi", "A" * 40)
        self.assertTrue(cut)
        self.check(text)

    def test_choose_drops_the_prefecture_first(self):
        v, text = addrdb.choose("Kagoshima", "Kirishima-shi", "Kokubunishikitaishimizu Higashi")
        self.assertGreaterEqual(v, 1)
        self.assertNotIn(b"Kagoshima", text)

    def test_short_city(self):
        self.assertEqual(addrdb.short_city("Nirasaki-shi"), "Nirasaki")
        self.assertEqual(addrdb.short_city("Sapporo Chuo-ku"), "Sapporo Chuo-ku")


class Data(unittest.TestCase):
    def test_tables_cover_the_database(self):
        rom = addrdb.ROM
        if not rom.exists():
            self.skipTest("ROM not present")
        db = addrdb.unpack(rom.read_bytes())
        pref, city, town = addrdb.load_en()
        self.assertEqual(len(pref), len(db["prefs"]))
        self.assertEqual(len(city), len(db["cities"]))
        for po, pr, ci, nm in db["towns"]:
            if nm:
                self.assertIn((pr, ci, nm), town, f"{po:07d}")
        for s in pref + city + list(town.values()):
            self.assertTrue(all(0x20 <= ord(c) < 0x7F for c in s) and "%" not in s, s)

    def test_pack_fits_and_points_into_the_pool(self):
        rom = addrdb.ROM
        if not rom.exists():
            self.skipTest("ROM not present")
        db = addrdb.unpack(rom.read_bytes())
        blob, e1, e2 = addrdb.pack_en(db, *addrdb.load_en())
        self.assertEqual(len(blob), addrdb.SLOT_END - addrdb.BASE)
        t, p, c, end = struct.unpack_from("<4I", blob, 0)
        self.assertEqual(t, 0x10)
        n = len(db["towns"])
        # the record past the last one is the scan's guard: postal code 0 never matches a parsed code
        self.assertEqual(blob[t + n * addrdb.EN_REC:t + (n + 1) * addrdb.EN_REC], bytes(addrdb.EN_REC))
        lo, hi = 0x08000000 + addrdb.BASE, 0x08000000 + addrdb.BASE + end
        for k in range(n):
            ptr = struct.unpack_from("<I", blob, t + k * addrdb.EN_REC + 7)[0]
            self.assertTrue(ptr == 0 or lo <= ptr < hi)
        self.assertEqual(e2 - e1, 8)


class PostalDash(unittest.TestCase):
    def test_pad_dash_stays_full_width(self):
        """The postal pad inserts t0B8B18 after 3 digits and the lookup converts it by its index in t0B8AC0
        (－ = 0x0B, the parser's dash); an ASCII '-' read as 0 and every code found its XXX-0000 record (v1.0)."""
        rows = json.loads((ROOT / "script" / "strings_0B8.json").read_text(encoding="utf8"))
        e = next(r for r in rows if r["id"] == "t0B8B18")
        self.assertEqual(e["jp"], "－")
        self.assertIn(e.get("en", ""), ("", "－"))


if __name__ == "__main__":
    unittest.main()
