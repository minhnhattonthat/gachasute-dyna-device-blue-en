import struct
import unittest
from pathlib import Path

import build
import script

ROOT = Path(__file__).resolve().parents[1]
ROMS = list((ROOT / "rom").glob("*.gba"))


@unittest.skipUnless(ROMS, "ROM not present")
class ScriptFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROMS[0].read_bytes()
        cls.scripts = script.unpack(cls.rom)

    def test_every_script_parses_and_repacks_identically(self):
        self.assertEqual(len(self.scripts), 834)
        self.assertEqual(script.pack(self.scripts), self.rom[script.BASE:script.END])

    def test_identity_build(self):
        self.assertEqual(bytes(build.build(self.rom)), self.rom)

    def test_message_text_roundtrips_cp932(self):
        n = 0
        for ops in self.scripts:
            for op in ops:
                if op.code == script.MSG:
                    self.assertEqual(op.text.decode("cp932").encode("cp932"), op.text)
                    n += 1
        self.assertGreater(n, 2800)

    def test_longer_text_keeps_jumps_on_their_ops(self):
        # every script with a jump: grow every message by 4 bytes (odd text is refused, see the next test), repack,
        # re-parse, and check each jump still lands on the op it hit before (same index in the op list)
        checked = 0
        for i, ops in enumerate(self.scripts):
            if not any(op.target is not None for op in ops) or not any(op.code == script.MSG for op in ops):
                continue
            index = {op.off: k for k, op in enumerate(ops)}
            want = [index[op.target] if op.target is not None else None for op in ops]
            grown = [op for op in ops if op.code == script.MSG and len(op.text) % 2 == 0]
            for op in grown:
                op.text += b"ABCD"
            try:
                again = script.parse_script(script.build_script(ops))
            finally:
                for op in grown:
                    op.text = op.text[:-4]
            index2 = {op.off: k for k, op in enumerate(again)}
            got = [index2[op.target] if op.target is not None else None for op in again]
            self.assertEqual(got, want, f"script {i}")
            self.assertEqual([op.code for op in again], [op.code for op in ops], f"script {i}")
            checked += 1
        self.assertGreater(checked, 50)

    def test_odd_length_text_is_refused(self):
        with self.assertRaises(ValueError):
            script.message_bytes(0, -1, b"abc")
        self.assertEqual(script.message_bytes(0, -1, b"ab"), b"\x02\x00\x00\x00\xff\xffab\x00\x00")

    def test_relocation_when_the_file_grows(self):
        out = bytearray(self.rom)
        blob = script.pack(self.scripts) + bytes(0x1000)
        at = build.place_script_file(out, blob)
        self.assertEqual(at, build.FREE_START)
        self.assertEqual(struct.unpack_from("<I", out, script.DIR_WORD)[0], 0x08000000 + at)
        self.assertEqual(len(script.unpack(bytes(out), at)), 834)


if __name__ == "__main__":
    unittest.main()
