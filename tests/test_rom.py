import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RomListing(unittest.TestCase):
    def test_rom_sha1_listing_is_filled(self):
        lines = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")]
        self.assertTrue(lines)
        for line in lines:
            sha, name = line.split(None, 1)
            self.assertRegex(sha, r"^[0-9a-f]{40}$")
            path = ROOT / name.strip()
            if not path.is_file():
                self.skipTest("ROM not present")
            self.assertEqual(hashlib.sha1(path.read_bytes()).hexdigest(), sha)


if __name__ == "__main__":
    unittest.main()
