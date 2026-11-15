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

    def test_map_patches_match_the_original(self):
        for off, old, new, why in gfx.MAP_PATCHES:
            self.assertEqual(list(struct.unpack_from(f"<{len(old)}H", self.rom, off)), old, why)
            self.assertEqual(len(old), len(new), why)

    def test_fortune_labels_have_their_own_tiles(self):
        """The fortune box's re-laid rows match the original SCR, and no two labels share a tile."""
        import gfx_text
        gfx.mini_patches(self.rom, gfx.FORTUNE_ROWS, "fortune")   # raises if a JP row or the SCR header differs
        seen = {}
        for scr in gfx_text.ATLASES[0x231524]["screens"]:
            text = scr["redraw"][0][0]
            for n in scr["cells"][0]:
                self.assertNotIn(n, seen, f"{text!r} and {seen.get(n)!r} share tile {n}")
                seen[n] = text

    def test_minigame_words_have_their_own_tiles(self):
        """Every small English word's tiles are shown by the re-laid minigame maps, no word shares a tile with
        another, and no kana tile the code writes beside numbers (てん, ふん, びょう) is reused for a word."""
        import gfx_text
        rows = gfx.mini_patches(self.rom)   # raises if a JP row or SCR header differs
        shown = {v & 0x3FF for _, _, new, _ in rows for v in new}
        seen = {}
        for text, tl in gfx_text.MINI_WORDS:
            for t in tl:
                self.assertNotIn(t, seen, f"{text!r} and {seen.get(t)!r} share tile {t}")
                seen[t] = text
                if text and len(tl) > 1:
                    self.assertIn(32 * t[0] + t[1], shown, f"{text!r} tile {t} is on no map")
        for code_tile in ((3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (5, 19)):
            self.assertNotIn(code_tile, gfx._S5)

    def test_distinct_survives_many_repeats(self):
        """0432534's PLT repeats magenta 11 times: distinct() must end and keep the first repeats' old colours."""
        out = gfx.distinct([(248, 0, 248)] * 11)
        self.assertEqual(len(set(out)), 11)
        self.assertEqual(out[:3], [(248, 0, 248), (248, 0, 249), (248, 0, 250)])

    def test_credits_pat_is_on_screen_and_relocated(self):
        """Staff roll (credits.py): 11 frames like the old PAT, every 8x16 letter inside the 240 px screen (anchor
        x 120), each glyph cell clear of the kept copyright mark, the new PAT parses back to the laid-out sprites,
        and one archive word (the one gfx.apply repoints) reaches the old PAT."""
        import credits
        import pat
        frames = credits.layout()
        self.assertEqual(len(frames), 11)
        for sp in frames:
            for x, y, t, size in sp:
                w = 16 if size == credits.SIZE_16X16 else 8
                self.assertTrue(-120 <= x and x + w <= 120, (x, t))
        slots = set(credits.glyphs().values())
        self.assertNotIn((2, credits.COPY[0]), slots)
        blob = credits.pat_blob()
        rom = bytearray(self.rom) + bytearray(len(blob))
        rom[len(self.rom):] = blob
        got = pat.frames(bytes(rom), len(self.rom))
        self.assertEqual([[(x, y, t) for _, _, _, x, y, t, _ in ents] for _, ents in got],
                         [[(x, y, t) for x, y, t, _ in sp] for sp in frames])
        self.assertEqual(gfx.archive_words(self.rom)[credits.PAT], [0x0EFEB4])

    def test_battle_board_titles_have_their_own_tiles(self):
        """With gfx.MAP_PATCHES applied, the Move title (PAT 025F094) no longer shares Place Dyna's tiles and the L
        Status frames (PAT 025F134 frames 0-1) show no tile at two x positions (the JP ス was drawn twice)."""
        import pat
        rom = bytearray(self.rom)
        for off, _, new, _ in gfx.MAP_PATCHES:
            struct.pack_into(f"<{len(new)}H", rom, off, *new)

        def tiles(off, frame):
            out = []
            for _, w, h, x, y, t, _ in pat.frames(rom, off)[frame][1]:
                out += [(t + 32 * r + c, x + 8 * c) for r in range(h // 8) for c in range(w // 8)]
            return out
        place = {t for t, _ in tiles(0x25F064, 0)}
        move = {t for t, _ in tiles(0x25F094, 0)}
        self.assertFalse(place & move, "Move Dyna title shares tiles with Place Dyna")
        for frame in (0, 1):
            pos = {}
            for t, x in tiles(0x25F134, frame):
                pos.setdefault(t, set()).add(x)
            self.assertTrue(all(len(v) == 1 for v in pos.values()), f"Status frame {frame}: {pos}")

    def test_menu_labels_on_maps_and_committed_png_current(self):
        import gfx_text
        img = gfx_text.render(self.rom, MENU)   # raises if a label is too wide or hits a blank column
        # every row label's tiles are what the patched submenu maps show
        rom = bytearray(self.rom)
        for off, _, new, _ in gfx.MAP_PATCHES:
            struct.pack_into(f"<{len(new)}H", rom, off, *new)
        shown = set()
        for scr in (0x1E3724, 0x1E3774, 0x1E37C4, 0x1E3834, 0x1E38A4):
            w, h = rom[scr + 5], rom[scr + 6]
            shown |= {v & 0x3FF for v in struct.unpack_from(f"<{w * h}H", rom, scr + 8)}
        for text, columns in gfx_text.ATLASES[MENU]["rows"]:
            for t in filter(None, columns):
                self.assertIn(t[0] * 32 + t[1], shown, text)
        png = gfx.GFX / f"{MENU:07X}.png"
        self.assertTrue(png.exists(), "run tools/gfx_text.py")
        from PIL import Image
        self.assertEqual(list(Image.open(png).convert("RGB").getdata()), list(img.getdata()),
                         "gfx/01E30D4.png is stale: run tools/gfx_text.py")


if __name__ == "__main__":
    unittest.main()
