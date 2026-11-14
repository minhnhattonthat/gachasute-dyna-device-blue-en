"""tools/lint.py rules, and the whole script/ lint-clean (the pre-commit check)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402


def msg(jp, en):
    return {"id": "s001.00", "jp": jp, "en": en}


class TestRules(unittest.TestCase):
    def errs(self, e, budgets=()):
        return lint.check_entry(e, list(budgets))[0]

    def test_fits(self):
        self.assertEqual(self.errs(msg("あ\nい{KP}\nう", "Hello there.\nSecond line.{KP}\nNext page.")), [])

    def test_too_wide(self):
        self.assertTrue(self.errs(msg("あ", "H" * 40)))          # 200 px > 176 (last line)
        self.assertEqual(self.errs(msg("あ\nい", "H" * 37 + "\nok")), [])   # 185 px <= 188 on a first line
        self.assertTrue(self.errs(msg("あ\nい", "ok\n" + "H" * 36)))       # 180 px > 176 on the last line

    def test_three_lines(self):
        self.assertTrue(self.errs(msg("あ", "a\nb\nc")))

    def test_codes(self):
        self.assertTrue(self.errs(msg("{%sR4}です", "Hi.")))
        self.assertEqual(self.errs(msg("{%sR4}です", "It's {%sR4}.")), [])
        self.assertTrue(self.errs(msg("あ{KN}", "Hi.")))

    def test_register_width(self):
        self.assertEqual(lint.line_width("{%sR4}"), lint.REG_PX["s"])
        self.assertEqual(lint.line_width("{%02dR1}"), 16)

    def test_string_budget(self):
        e = {"id": "t0B0000", "jp": "あ", "en": "H" * 10}
        self.assertTrue(self.errs(e, [(0xB0000, 0xB0000, 40, 1, "test")]))
        self.assertEqual(self.errs(e, [(0xB0000, 0xB0000, 50, 1, "test")]), [])


class TestScript(unittest.TestCase):
    def test_script_clean(self):
        budgets = lint.load_budgets()
        bad = []
        for f in sorted(lint.SCRIPT.glob("*.json")):
            for e in json.loads(f.read_text(encoding="utf-8")):
                errs, _ = lint.check_entry(e, budgets)
                bad += [f"{e['id']}: {x}" for x in errs]
        self.assertEqual(bad, [], "\n".join(bad[:20]))


if __name__ == "__main__":
    unittest.main()
