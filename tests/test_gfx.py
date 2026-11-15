import random
import struct
import tempfile
import unittest
from pathlib import Path

import ecd
import gfx

ROOT = Path(__file__).resolve().parents[1]
ROMS = list((ROOT / "rom").glob("*.gba"))
MENU = 0x1E30D4   # field menu bar atlas


@unittest.skipUnless(ROMS, "needs the original ROM in rom/")
class Gfx(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROMS[0].read_bytes()

    def test_archive_references_every_block(self):
        words = gfx.archive_words(self.rom)
        self.assertTrue({b[0] for b in ecd.scan(self.rom)} <= set(words))
        self.assertIn(MENU, words)

    def test_png_roundtrip_is_identity(self):
        raw = ecd.decompress(self.rom, MENU)[0]
        pal, _ = gfx.palette_for(self.rom, MENU)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.png"
            gfx.to_png(raw, pal).save(p)
            self.assertEqual(gfx.from_png(p, raw, pal), raw)

    def test_grown_block_is_relocated(self):
        raw = ecd.decompress(self.rom, MENU)[0]
        pal, _ = gfx.palette_for(self.rom, MENU)
        img = gfx.to_png(raw, pal)
        # noise in palette colours compresses badly, so the block must move
        px = img.load()
        rnd = random.Random(1)
        for y in range(img.height):
            for x in range(img.width):
                px[x, y] = pal[rnd.randrange(10)]
        with tempfile.TemporaryDirectory() as d:
            old = gfx.GFX
            gfx.GFX = Path(d)
            try:
                img.save(Path(d) / f"{MENU:07X}.png")
                out = bytearray(self.rom)
                free = 0x7E0000
                nxt = gfx.apply(self.rom, out, free, None, limit=0x7F0000)
            finally:
                gfx.GFX = old
        self.assertGreater(nxt, free)
        for w in gfx.archive_words(self.rom)[MENU]:
            self.assertEqual(gfx.ARC + struct.unpack_from("<I", out, w)[0], free)
        new = ecd.decompress(bytes(out), free)[0]
        self.assertEqual(len(new), len(raw))
        self.assertEqual(list(gfx.to_png(new, pal).getdata()), list(img.getdata()))


if __name__ == "__main__":
    unittest.main()
