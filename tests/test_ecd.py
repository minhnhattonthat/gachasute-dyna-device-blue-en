import unittest
from pathlib import Path

import ecd

ROOT = Path(__file__).resolve().parents[1]
ROMS = [p for p in [ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"] if p.exists()]   # not Red's dump


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

    def test_encoder_reproduces_the_original_blocks(self):
        # every 8th block keeps the check fast (all 3114 match: `python -X utf8 tools/ecd.py verify ROM`, ~30 s)
        for off, in_len, _ol, _tag in self.blocks[::8]:
            raw, _ = ecd.decompress(self.data, off)
            self.assertEqual(ecd.compress(raw), self.data[off:off + 16 + in_len], hex(off))


if __name__ == "__main__":
    unittest.main()
