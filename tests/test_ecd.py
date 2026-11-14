import unittest
from pathlib import Path

import ecd

ROOT = Path(__file__).resolve().parents[1]
ROMS = list((ROOT / "rom").glob("*.gba"))


@unittest.skipUnless(ROMS, "ROM not present")
class EcdBlocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ROMS[0].read_bytes()
        cls.blocks = ecd.scan(cls.data)

    def test_block_count(self):
        self.assertEqual(len(self.blocks), 3114)

    def test_every_block_decodes_to_declared_size_and_roundtrips(self):
        for off, _il, out_len, _tag in self.blocks:
            raw, _ = ecd.decompress(self.data, off)
            self.assertEqual(len(raw), out_len, hex(off))
            self.assertEqual(ecd.decompress(ecd.compress_stored(raw), 0)[0], raw, hex(off))


if __name__ == "__main__":
    unittest.main()
