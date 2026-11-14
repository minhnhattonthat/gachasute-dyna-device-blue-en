"""check.py: the repo's one-command check (all tests + text lint). The pre-commit hook runs it.

Runs every tests/test_*.py with unittest; exit code is non-zero on any failure.
Tests that need the ROM skip themselves when rom/ is missing (a fresh clone without the dump)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT / "tools"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
