import unittest
from pathlib import Path

import build
import insert
import romwrite

ROOT = Path(__file__).resolve().parents[1]
ROMS = list((ROOT / "rom").glob("*.gba"))


class Gate(unittest.TestCase):
    def test_write_outside_ranges_fails(self):
        orig = bytes(64)
        out = bytearray(orig)
        log = romwrite.Log(orig)
        log.put(out, 8, b"\1\2", "inside")
        log.put(out, 30, b"\3\4\5", "straddles")
        errs = romwrite.verify(orig, out, log, ranges=[(0, 15), (28, 31)])
        self.assertEqual(len(errs), 1)
        self.assertIn("straddles", errs[0])
        self.assertIn("0x000020", errs[0])

    def test_touching_ranges_cover_a_write(self):
        log = romwrite.Log(bytes(16))
        out = bytearray(16)
        log.put(out, 2, b"\1" * 8, "w")
        self.assertEqual(romwrite.verify(bytes(16), out, log, ranges=[(0, 5), (6, 9), (4, 12)]), [])

    def test_unlogged_change_fails(self):
        orig = bytes(16)
        out = bytearray(orig)
        log = romwrite.Log(orig)
        out[3] = 1
        self.assertTrue(romwrite.verify(orig, out, log, ranges=[(0, 15)]))


@unittest.skipUnless(ROMS, "ROM not present")
class EnglishBuild(unittest.TestCase):
    """The English build (built here, not read from build/) writes only where tools/allowed_ranges.txt and the
    extracted pointer words allow, over the original bytes it expects, with no write overwritten."""

    def test_english_build_passes_romdiff(self):
        rom = ROMS[0].read_bytes()
        entries = insert.load_entries()
        log = romwrite.Log(rom)
        report = {}
        out = build.build(rom, insert.message_scripts(rom, entries), english=True, entries=entries, log=log,
                          report=report)
        self.assertEqual(romwrite.verify(rom, out, log), [])
        # every string with English is written (no table silently skipped)
        want = sum(1 for e in entries.values() if e["id"].startswith("t") and e.get("en"))
        self.assertEqual(report["strings_in_place"] + report["strings_moved"], want)
        self.assertEqual(sum(1 for r in log.rows if r[3].startswith("string ")), want)

    def test_moved_strings_leave_no_pointer_behind(self):
        """Every aligned word in the original ROM that points at a moved string's start (0x08 in bits 24-27, any
        flag bits above) is one of the pointer words the build rewrites (script/ "ptrs")."""
        import struct
        rom = ROMS[0].read_bytes()
        entries = insert.load_entries()
        moved = {}
        for e in entries.values():
            if e["id"].startswith("t"):
                raw = insert.string_bytes(e, False)
                if raw is not None and len(raw) > e["slot"]:
                    moved[0x08000000 + int(e["id"][1:], 16)] = e
        self.assertTrue(moved)
        coincidences = {0x09EE48,   # Thumb code 0x6028 0x480B: str r0,[r5]; ldr r0,[pc,#0x2c]
                        0x53B38C}   # inside the address database (0x44C754-0x702BB4), 0x480B9000
        stale = []
        for i, w in enumerate(struct.unpack(f"<{len(rom) // 4}I", rom)):
            e = moved.get(w & 0x0FFFFFFF) if (w >> 24) & 0xF == 8 and i * 4 not in coincidences else None
            if e is not None and f"{i * 4:06X}" not in {p.upper().zfill(6) for p in e["ptrs"]}:
                stale.append(f"{i * 4:#x} -> {e['id']}")
        self.assertEqual(stale, [])

    def test_hook_swallows_no_branch_target(self):
        """No Thumb branch within 4 KB lands inside the 8 bytes the VWF hook overwrites (0x080049AC)."""
        try:
            import capstone
        except ImportError:   # a required dependency: fail, never skip silently (pipeline.md §Checks)
            self.fail("capstone not installed: pip install capstone")
        import vwf
        rom = ROMS[0].read_bytes()
        md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
        md.skipdata = True
        lo, hi = vwf.HOOK_AT - 0x1000, vwf.HOOK_AT + 0x1000
        inside = range(vwf.BUS + vwf.HOOK_AT + 1, vwf.BUS + vwf.HOOK_AT + 8)
        hits = []
        for start in (lo, lo + 2):
            for i in md.disasm(rom[start:hi], vwf.BUS + start):
                if i.mnemonic.startswith(("b", "cb")) and i.op_str.startswith("#"):
                    if int(i.op_str[1:], 16) in inside:
                        hits.append(f"{i.address:#x} {i.mnemonic} {i.op_str}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
