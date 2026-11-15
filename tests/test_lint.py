"""tools/lint.py rules, and the whole script/ lint-clean (the pre-commit check)."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import budgets  # noqa: E402
import lint  # noqa: E402
import vwf  # noqa: E402


class TestBudgets(unittest.TestCase):
    def test_budgets_file_current(self):
        """docs/re/budgets.tsv = tools/budgets.py output (edit the window table there, then regenerate)."""
        self.assertEqual(budgets.OUT.read_text(encoding="utf-8"), budgets.render())

    def test_every_todo_string_has_a_budget(self):
        rows = lint.load_budgets()
        for f in (ROOT / "script").glob("strings_*.json"):
            for e in json.loads(f.read_text(encoding="utf-8")):
                if e["status"] == "todo":
                    self.assertIsNotNone(lint.budget_for(e["id"], rows), e["id"])


def msg(jp, en):
    return {"id": "s001.00", "jp": jp, "en": en}


class TestRules(unittest.TestCase):
    def errs(self, e, budgets=()):
        return lint.check_entry(e, list(budgets))[0]

    def test_fits(self):
        self.assertEqual(self.errs(msg("あ\nい{KP}\nう", "Hello there.\nSecond line.{KP}\nNext page.")), [])

    def test_too_wide(self):
        self.assertTrue(self.errs(msg("あ", "H" * 40)))          # 200 px > 176 (last line)
        self.assertEqual(self.errs(msg("あ\nい", "H" * 37 + "\nokay ok")), [])   # 185 px <= 188 on a first line
        self.assertTrue(self.errs(msg("あ\nい", "ok\n" + "H" * 36)))       # 180 px > 176 on the last line

    def test_stub_last_line(self):
        self.assertTrue(self.errs(msg("あ\nい", "A long first line here\nok.")))
        self.assertEqual(self.errs(msg("あ{%sR4}\nい", "A long first line here\nto {%sR4}.")), [])
        self.assertEqual(self.errs(msg("あ", "ok.")), [])                  # a one-line page is no stub

    def test_three_lines(self):
        self.assertTrue(self.errs(msg("あ", "a\nb\nc")))

    def test_codes(self):
        self.assertTrue(self.errs(msg("{%sR4}です", "Hi.")))
        self.assertEqual(self.errs(msg("{%sR4}です", "It's {%sR4}.")), [])
        self.assertTrue(self.errs(msg("あ{KN}", "Hi.")))

    def test_register_width(self):
        self.assertEqual(lint.line_width("{%sR4}"), lint.REG_PX["s"])
        self.assertEqual(lint.line_width("{%02dR1}"), 16)

    def test_raw_byte_width(self):
        self.assertEqual(lint.line_width("a[5C]b"), vwf.width("a\\b"))
        self.assertEqual(lint.line_width("[7F]"), 0)

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
