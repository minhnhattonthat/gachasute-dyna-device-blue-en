import unittest

from tools import batches


class TestBatches(unittest.TestCase):
    def test_selftest(self):
        root, tl, script, glossary = batches.ROOT, batches.TL, batches.SCRIPT, batches.GLOSSARY
        try:
            batches._selftest()
        finally:
            batches.ROOT, batches.TL, batches.SCRIPT, batches.GLOSSARY = root, tl, script, glossary

    def test_shipped_english(self):
        self.assertEqual(batches.main(["check"]), 0)


if __name__ == "__main__":
    unittest.main()
