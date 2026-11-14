"""VWF font, English encoder and hook (tools/vwf.py, docs/re/font.md)."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import insert  # noqa: E402
import vwf  # noqa: E402
from text import TOKEN  # noqa: E402

ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
SAMPLES = [
    "Hello!", "KGB agent", "C3PO and C4", "A\nB{KP}\nCD", "Hi {%sR0}, OK?", "x{%02dR1}y", "Ａx", "x Ａ",
    "Welcome to Dyna City! The quick brown\nfox jumps over the lazy dog.{KN}", "{C1}Red{C0} text",
]


def segments(raw):
    """Split encoded bytes at even-aligned codes -> list of segment byte strings (register codes removed)."""
    out, cur, i = [], bytearray(), 0
    while i < len(raw):
        if i % 2 == 0 and raw[i:i + 2] in vwf.CODES:
            out.append(bytes(cur))
            cur = bytearray()
            i += 2
            continue
        m = re.compile(rb"%(?:s|\d*d)R\d").match(raw, i)
        if m and i % 2 == 0:
            i = m.end()
            continue
        cur.append(raw[i])
        i += 1
    out.append(bytes(cur))
    return out


class TestFont(unittest.TestCase):
    def test_glyphs(self):
        f = vwf.font()
        for c in range(0x20, 0x7F):
            ch = chr(c)
            if ch in "\\`{}[]|^_<>@#$%~":
                continue
            self.assertIn(ch, f, f"missing glyph {ch!r}")
            adv, rows = f[ch]
            self.assertTrue(2 <= adv <= 9, ch)
            self.assertEqual(len(rows), 8)

    def test_tables(self):
        w, g = vwf.tables()
        self.assertEqual(len(w), 96)
        self.assertEqual(w[vwf.PAD - 0x20], 0)
        self.assertEqual(len(g), 96 * 8)


class TestEncode(unittest.TestCase):
    def check(self, s):
        raw = vwf.encode_en(s)
        self.assertEqual(len(raw) % 2, 0, s)
        # the only even-aligned code units are the ones the source asked for
        want = re.findall(r"\{KP\}\n?|\{KN\}|\{C\d\}|\n", s)
        got = [raw[i:i + 2] for i in vwf.code_units(raw)]
        self.assertEqual(len(got), len(want), (s, raw))
        # SJIS chars start on even bytes; every segment has units * 8 >= its pixel width
        for seg in segments(raw):
            px, i = 0, 0
            while i < len(seg):
                b = seg[i]
                if b >= 0x81:
                    self.assertEqual(i % 2, 0, (s, seg))
                    px += 8
                    i += 2
                    continue
                if 0x20 <= b < 0x7F:
                    px += vwf.char_width(chr(b))
                i += 1
            self.assertGreaterEqual(len(seg) // 2 * 8, px, (s, seg))
        return raw

    def test_samples(self):
        for s in SAMPLES:
            self.check(s)

    def test_code_pairs_split(self):
        raw = self.check("KGKPKN")
        self.assertEqual(vwf.code_units(raw), [])

    def test_register_even(self):
        raw = vwf.encode_en("abc{%sR4}d")
        self.assertEqual(raw.index(b"%") % 2, 0)

    def test_bad_char(self):
        with self.assertRaises(ValueError):
            vwf.encode_en("a{b")


@unittest.skipUnless(ROM.exists(), "needs rom/")
class TestHook(unittest.TestCase):
    def test_apply(self):
        rom = bytearray(ROM.read_bytes())
        orig = bytes(rom[vwf.HOOK_AT:vwf.HOOK_AT + 8])
        self.assertEqual(orig[:2], bytes.fromhex("f0b5"))  # push {r4-r7, lr}: the entry the hook replaces
        vwf.apply(rom)
        self.assertEqual(rom[vwf.HOOK_AT:vwf.HOOK_AT + 4], bytes.fromhex("00490847"))
        self.assertEqual(int.from_bytes(rom[vwf.HOOK_AT + 4:vwf.HOOK_AT + 8], "little"), vwf.BUS + vwf.VWF_AT)


class TestMarkers(unittest.TestCase):
    def test_every_entry_encodes(self):
        entries = insert.load_entries()
        if not entries:
            self.skipTest("no script/")
        for e in entries.values():
            if e.get("status") != "todo":
                continue
            txt = insert.marker(e["id"], e["jp"]) if e["id"].startswith("s") else insert.string_marker(e)
            vwf.encode_en(txt)
            if e.get("en"):
                vwf.encode_en(e["en"])


if __name__ == "__main__":
    unittest.main()
