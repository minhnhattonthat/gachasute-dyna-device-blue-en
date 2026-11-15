"""gfx.py: graphics text - export ECD IMG blocks to PNG and put edited PNGs back into the build.

    python -X utf8 tools/gfx.py export OFF [OFF..]   # work/gfx/orig/OFF.png (1x) and OFF_x4.png, palette = next PLT
    python -X utf8 tools/gfx.py check                # every gfx/*.png converts (palette, size); prints sizes

Every ECD block lives in archive 0 of the resource table at 0x080BBDE8 (docs/re/compression.md): the archive at
ROM 0x0E7FA4 starts with u32 offsets relative to itself, and the loader (0x08003074) reads block = base + off[i].
An edited block is written in its old slot when it fits (up to the next block), else into free space with every
archive word that pointed at it rewritten. One English image per block: gfx/<OFFSET>.png (7 hex digits, the ECD
block offset as in docs/re/graphics.md), same size as the original, drawn only in the colours of its palette.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import romwrite  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Gachasute! Dyna Device Blue (Japan).gba"
GFX = ROOT / "gfx"
ARC = 0x0E7FA4          # archive 0: every ECD block

# u16 map (SCR) entries fixed alongside the art: (ROM offset, original words, English words, why). Written by
# apply() whenever gfx/ holds a PNG; the original words are checked so a wrong offset fails the build.
# Field menu atlas 01E30D4 (entries = atlas row*32+col, 0x1FF = blank tile; tools/gfx_text.py draws the labels):
# "Save" and "Sort" fit 4 tiles, which frees 1,21 for the bar's Database button (the JP map used the frame-only 4,12,
# also the submenus' bottom frame) and 2,13 / 2,18 to widen Keywords to 6 tiles.
MAP_PATCHES = [
    (0x1E365A, [0x08C], [0x035], "menu bar SCR 01E3644: Database bottom col 1 -> 1,21"),
    (0x1E372C, [0x040, 0x041, 0x042, 0x043, 0x044, 0x035], [0x1FF, 0x040, 0x041, 0x042, 0x043, 0x1FF],
     "System submenu SCR 01E3724 row 0: Save in 2,0-2,3"),
    (0x1E3794, [0x04D, 0x04E, 0x04F, 0x050, 0x051, 0x052], [0x1FF, 0x04E, 0x04F, 0x050, 0x051, 0x1FF],
     "Items submenu SCR 01E3774 row 2: Sort in 2,14-2,17"),
    (0x1E38DC, [0x1FF, 0x088, 0x089, 0x08A, 0x08B, 0x1FF], [0x04D, 0x088, 0x089, 0x08A, 0x08B, 0x052],
     "Database submenu SCR 01E38A4 row 4: Keywords in 2,13 4,8-4,11 2,18"),
    # Team setup menu SCR 0x3B2854 (block 03B25A4 tiles, word = 32 * row + col; tools/gfx_text.py draws the runs)
    (0x3B2876, [0x08, 0x09, 0x0A, 0x27, 0x09, 0x28, 0x0A, 0x29], [0x08, 0x09, 0x0A, 0x27, 0x28, 0, 0, 0],
     "team menu SCR 03B2854 row 1: Add/Swap in 0,8-0,10 1,7 1,8"),
    (0x3B28A6, [0x47, 0x48, 0x49, 0], [0x29, 0x47, 0x48, 0x49], "team menu SCR 03B2854 row 3: Remove in 1,9 2,7-2,9"),
    (0x3B28D6, [0x67, 0x68, 0x69, 0x09], [0x67, 0x68, 0x69, 0], "team menu SCR 03B2854 row 5: Done in 3,7-3,9"),
    # Battle placement sprites (block 025E304 at OBJ tile 0, PAT frames listed by tools/pat.py 25F004): the Move
    # title ダイナ+いどう reused ダイナはいち's first 5 tiles; give it the free r0-1 c10-14 so both titles are whole
    # English ("Place Dyna" c0-9, "Move Dyna" c10-14 + c16-20). L button ステータス repeats ス (r5 c29) at x 9:
    # put that sprite on top of the first one (x -23, same tile) so "Status" is one 4-tile run.
    (0x25F0B2 + 6, [0x3004], [0x300E], "PAT 025F094 Move title: 8x16 r0 c4 -> r0 c14"),
    (0x25F0BA + 6, [0x3000], [0x300A], "PAT 025F094 Move title: 32x16 r0 c0 -> r0 c10"),
    (0x25F156 + 2, [9], [0xFFE9], "PAT 025F134 frame 0 (L Status, pal 1): repeated ス x 9 -> -23"),
    (0x25F188 + 2, [9], [0xFFE9], "PAT 025F134 frame 1 (L Status, pal 2): repeated ス x 9 -> -23"),
    # PDA calendar month header (raw SCR at 0x217E54, 30x20 words from +8; block 0215E74 tiles): 年 becomes "/" in
    # the art, the 月 unit cells (row 3-4, col 21-22) go blank: "2000年 0月" -> "2000/ 0".
    (0x217F3A, [0x10D4, 0x10D5], [0x1000, 0x1000], "calendar header SCR 0217E54 row 3: no 月 unit"),
    (0x217F76, [0x10F4, 0x10F5], [0x1000, 0x1000], "calendar header SCR 0217E54 row 4: no 月 unit"),
    # Day view header "0月 0日 (月) の予定" (raw SCR 0x2197F4): the 月 / 日 units are the 16x16 weekday glyphs, now
    # Su..Sa: 月 -> the header's "/" (年 tiles 4,2), 日 -> blank, の予定 redrawn as "Plans": "12/31 (Mo) Plans".
    (0x2198BE, [0x10D4, 0x10D5], [0x1082, 0x1083], "calendar day view SCR 02197F4 row 3: 月 unit -> /"),
    (0x2198FA, [0x10F4, 0x10F5], [0x10A2, 0x10A3], "calendar day view SCR 02197F4 row 4: 月 unit -> /"),
    (0x2198CA, [0x10D2, 0x10D3], [0x0000, 0x0000], "calendar day view SCR 02197F4 row 3: no 日 unit"),
    (0x219906, [0x10F2, 0x10F3], [0x0000, 0x0000], "calendar day view SCR 02197F4 row 4: no 日 unit"),
]
# PDA money diary dates (block 021C414; docs/re/graphics.md "Money diary dates"). Glyphs are drawn by 0x0802DF10
# (r1 = glyph index into the table at 0x080D2590: u16 tile|pal<<12, u16 kind 0=16x16 1=8x16 2=8x8). The date units
# 月 / 日 are the weekday glyphs 24 / 23, so they can't become "/" in the art: the unit calls change instead.
# Day view "12月31日 (土)" -> "12/31 (Sa)": 月 -> new glyph 33, a 16x16 "/" in the free tiles 3,14-4,15 (every
# entry 0-32 is in use, 22 = the list rows' end dot: the table moves to free space with one more entry, its only
# pointer is the pool word 0x0802DF68), the 日 call -> nops. Month views "2000年 12月" -> "2000/12": the 月 calls
# -> nops (the small 年 glyph is drawn as "/").
NOP2 = [0x46C0, 0x46C0]
GLYPHS, GLYPHS_N, GLYPHS_PTR = 0x0D2590, 33, 0x02DF68
SLASH = [0x106E, 0x0000]   # glyph 33: tile 3,14 (0x6E) pal 1, 16x16
DATE_PATCHES = [
    (0x030B92, [0x2118], [0x2121], "money diary day view: 月 unit -> glyph 33 '/'"),
    (0x030BFC, [0xF7FD, 0xF988], NOP2, "money diary day view: no 日 unit"),
    (0x02E21E, [0xF7FF, 0xFE77], NOP2, "money diary week view: no 月 unit"),
    (0x030408, [0xF7FD, 0xFD82], NOP2, "money diary month view: no 月 unit (1-digit month)"),
    (0x030464, [0xF7FD, 0xFD54], NOP2, "money diary month view: no 月 unit (2-digit month)"),
]
# PDA timetable palette status line "月曜日 1時間目 = [icon]" (PAT at 0x22F194, block 022CF64; entries u16 size,
# s16 x, s16 y, u16 tile, screen x = 120 + x) -> "Mon, period 1 = [icon]": weekday frames (Mon..Sat) move the
# weekday to x84 and the 曜日 16x16 piece (now ",") to x100; digit frames (1..7) move the 時間目 32x16 piece (now
# "period") to x106, the digit to x133 and "=" to x141 (the 時間目 and 曜日 8x16 tails are blank).
TT_DAYS = [0x22F246, 0x22F260, 0x22F27A, 0x22F294, 0x22F2AE, 0x22F2C8]
TT_DIGITS = [0x22F2E2 + 0x22 * n for n in range(7)]


def tt_patches(rom):
    out = []
    for k, f in enumerate(TT_DAYS):
        for i in range(3):
            e = f + 2 + 8 * i
            tile = struct.unpack_from("<H", rom, e + 6)[0] & 0x3FF
            new = {128 + 2 * k: -36, 140: -20}.get(tile)
            if new is not None:
                old = struct.unpack_from("<h", rom, e + 2)[0]
                out.append((e + 2, [old & 0xFFFF], [new & 0xFFFF], f"timetable weekday frame {k}: tile {tile} x"))
    for n, f in enumerate(TT_DIGITS):
        for i in range(4):
            e = f + 2 + 8 * i
            tile = struct.unpack_from("<H", rom, e + 6)[0] & 0x3FF
            new = {144 + n: 13, 143: 21, 151: -14}.get(tile)
            if new is not None:
                old = struct.unpack_from("<h", rom, e + 2)[0]
                out.append((e + 2, [old & 0xFFFF], [new & 0xFFFF], f"timetable digit frame {n}: tile {tile} x"))
    if len(out) != 6 * 2 + 7 * 3:
        raise ValueError(f"timetable PAT: {len(out)} entries found, expected 33")
    return out

# Title screen planet name (block 0449734, OBJ 2D, OBJ tile n = block tile n). Sprite frames 3-12 of the title's
# PAT animation at 0x44BF24 (u32 offsets from it at +8) each hold 8 OAM entries (u16 size code | 0x2000, s16 x,
# s16 y, u16 tile | pal << 12); the name is a 32x8 piece at x 8, a second piece at x 40 and the bar's end cap
# (tile 413) at x 48, all 40 px bars in JP. English: (frame, name, atlas tile row, first column, tiles): a 32x8 +
# 8x8 / 16x8 / 32x8 piece, the cap at x 8 + 8 * tiles; 7 tiles = two 32x8 pieces whose last tile is left
# transparent under the cap. tools/gfx_text.py paints the runs.
TITLE_ANIM = 0x44BF24
TITLE_NAMES = [
    (3, "Terioranus", 10, 8, 6), (4, "Sigmazon", 10, 20, 5), (5, "Capuchipean", 10, 0, 7),
    (6, "Bisaios", 10, 25, 5), (7, "Jornaturn", 10, 14, 6), (8, "Parmoon", 11, 0, 5), (9, "Plutario", 11, 5, 5),
    (10, "Mercurie", 11, 10, 5), (11, "Byjupiter", 11, 15, 5), (12, "Zaurak", 11, 20, 5),
]
SIZE_CODE = {5: 0x00, 6: 0x41, 7: 0x52}   # second piece: 8x8, 16x8, 32x8


def title_patches(rom):
    """MAP_PATCHES-style rows for the planet name entries of title frames 3-12."""
    out = []
    for frame, name, row, col, n in TITLE_NAMES:
        p = TITLE_ANIM + struct.unpack_from("<I", rom, TITLE_ANIM + 8 + 4 * frame)[0]
        if struct.unpack_from("<h", rom, p)[0] != 8:
            raise ValueError(f"title frame {frame}: expected 8 OAM entries")
        start = 32 * row + col
        ents = {struct.unpack_from("<h", rom, p + 4 + 8 * i)[0]: p + 2 + 8 * i for i in range(8)}
        for x, attr, nx, tile in ((8, None, 8, start), (40, SIZE_CODE[n], 40, start + 4), (48, None, 8 + 8 * n, 413)):
            e = ents[x]
            old = list(struct.unpack_from("<4H", rom, e))
            new = [old[0] if attr is None else (old[0] & 0xFF00) | attr, nx, old[2], (old[3] & 0xFC00) | tile]
            if x == 48 and old[3] & 0x3FF != 413:
                raise ValueError(f"title frame {frame}: no end cap at x 48")
            out.append((e, old, new, f"title frame {frame} {name}: piece at x {x}"))
    return out


# Minigame screens (docs/re/graphics.md "Minigames"): raw SCR maps (header 'SCR\0', u8 0, u8 w, u8 h, u8 0, then
# w*h u16 words = 32 * atlas row + atlas col | pal << 12) for blocks 03D5DB4 (big words + small charset) and 03D7FD4
# (help header + small words). Full map rows: (SCR offset, row, JP tiles, English tiles, why); tiles are (row, col)
# or None for blank word 0. The JP tiles are checked, the palette bits are kept from the row's first JP tile.
_ = None
_G = [(8, 11), (8, 12), (8, 13), (4, 26), (8, 14), (8, 15)]   # ゲーム -> "Game" over the same 6 tiles
_GB = [(9, 11), (9, 12), (9, 13), (5, 26), (9, 14), (9, 15)]
_S5 = [(3, 5), (3, 6), (3, 7), (3, 9), (3, 10), (3, 11)] + [(4, c) for c in range(16)] + [(5, c) for c in range(19)] \
    + [(6, c) for c in range(5)]   # 03D5DB4 small kana tiles freed for English words (gfx_text MINI_WORDS order)
MINI_ROWS = [
    (0x3D6DF4, 1, [_] + _G+ [(8, c) for c in range(16, 24)], [_, _] + _G + [(8, c) for c in range(16, 22)] + [_],
     "title button Game Start"),
    (0x3D6DF4, 2, [_] + _GB + [(9, c) for c in range(16, 24)], [_, _] + _GB + [(9, c) for c in range(16, 22)] + [_],
     "title button Game Start (bottom)"),
    (0x3D7A04, 1, [_] + _G+ [(4, c) for c in range(20, 28)], [_, _] + _G + [(4, c) for c in range(20, 26)] + [_],
     "Game Over (4,26 now belongs to Game)"),
    (0x3D7A04, 2, [_] + _GB + [(5, c) for c in range(20, 28)], [_, _] + _GB + [(5, c) for c in range(20, 26)] + [_],
     "Game Over (bottom)"),
    (0x3D7954, 1, [_] * 4 + [(8, c) for c in range(16, 23)] + [(8, 24)],
     [_] * 5 + [(8, c) for c in range(16, 22)] + [(8, 24)], "Start!"),
    (0x3D7954, 2, [_] * 4 + [(9, c) for c in range(16, 23)] + [(9, 24)],
     [_] * 5 + [(9, c) for c in range(16, 22)] + [(9, 24)], "Start! (bottom)"),
    (0x3D79A4, 1, [_] * 2 + [(8, c) for c in range(11)] + [(8, 24)], [_] * 3 + [(8, c) for c in range(9)] + [(8, 24), _],
     "Time Up!"),
    (0x3D79A4, 2, [_] * 2 + [(9, c) for c in range(11)] + [(9, 24)], [_] * 3 + [(9, c) for c in range(9)] + [(9, 24), _],
     "Time Up! (bottom)"),
    (0x3D71D4, 0, [(5, 5), (3, 1), (5, 7), (5, 0), (5, 17), _, (5, 3), (6, 3), (5, 4)],
     [_] + _S5[0:3] + _S5[3:6] + [_, _], "げんざいの きろく -> High Score"),
    (0x3D71F4, 0, [(5, 14), (5, 4), (3, 0), (3, 1)], _S5[3:6] + [_], "とくてん -> Score"),
    (0x3D7204, 0, [(4, 3), (4, 12), (4, 0), (4, 6), (4, 1), (4, 11)], _S5[6:12], "クリアタイム -> Clear Time"),
    (0x3D7224, 0, [(5, 8), (3, 1), (5, 3), (6, 3), (5, 4), (3, 9), (3, 9)], _S5[12:19], "しんきろく！！ -> New Record!"),
    (0x3D7244, 0, [(5, 6), (3, 1), (5, 2), (5, 0), _, (3, 0), (5, 16), (5, 18), (5, 0), (5, 13), (5, 11), _,
                   (3, 5), (3, 6), (3, 7)], _S5[19:25] + [_] * 9, "こんかい てにはいった ビット -> Bits Earned"),
    (0x3D7274, 0, [(5, 5), (3, 1), (5, 7), (5, 0), _, (6, 2), (5, 13), (3, 0), (5, 0), (6, 4), _, (3, 5), (3, 6),
                   (3, 7)], _S5[25:30] + [_] * 9, "げんざい もっている ビット -> Your Bits"),
    (0x3D7364, 1, [_] * 4 + [(4, 2), (4, 8), (4, 0), (3, 6), (4, 9), (5, 8), (6, 1), (5, 9), (5, 2), (3, 10)] + [_] * 3,
     [_] * 6 + _S5[30:35] + [_] * 6, "ギブアップしますか？ -> Give up?"),
    (0x3D7364, 3, [_, (5, 18), (5, 0), (3, 8), (7, 0), (4, 10), (4, 6), (4, 15), _, (5, 0), (5, 0), (5, 1), (3, 8),
                   (7, 1), (4, 10), (4, 6), (4, 15)],
     [_] * 3 + [(7, 0), (3, 8)] + _S5[35:37] + [_, _, (7, 1), (3, 8)] + _S5[37:39] + [_] * 4, "A=Yes  B=No"),
    (0x3D7474, 1, [_, (5, 15), (5, 17), (4, 14), (6, 0), (4, 13), (5, 16), _, (5, 12), (3, 3), (3, 4), (5, 10), (3, 1),
                   (5, 8), (6, 1), (5, 9), (5, 2), (3, 10)],
     [_] * 5 + _S5[39:46] + [_] * 6, "どのレベルに ちょうせんしますか？ -> Which level?"),
    # block 03D7FD4: title / level-select R legend and the how-to-play page labels
    (0x3D8704, 0, [_, (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), _, (0, 6), (0, 7), (0, 8), _, (0, 9), (0, 10), (0, 11),
                   (0, 12), _, (0, 13), (0, 14), (0, 15), (0, 16), (0, 5), _, (0, 17), (0, 18), (1, 16), (1, 17),
                   (1, 18), (2, 16), (0, 7), _],
     [_] * 8 + [(0, c) for c in range(1, 6)] + [_] + [(0, c) for c in range(6, 13)] + [_] * 9,
     "R line: Rボタンを おすと ゲームの せつめいを ひょうじします -> R Button  How to Play"),
    (0x3D8754, 0, [(0, 1), (0, 2), (0, 3), (0, 4)] + [_] * 5, [(0, c) for c in range(1, 6)] + [_] * 4,
     "level select legend: Rボタン -> R Button"),
    (0x3D8754, 1, [(0, 9), (0, 10), (0, 11), (0, 12), _, (0, 13), (0, 14), (0, 15), (0, 16)],
     [(0, c) for c in range(6, 13)] + [_, _], "level select legend: ゲームの せつめい -> How to Play"),
    # how-to-play page SCR 3D8784 (30x20): (row, first col) segments
    (0x3D8784, (4, 3), [(2, 17), (1, 16), (2, 18), (5, 5), (1, 16), (5, 5), (1, 16)],
     [(0, c) for c in range(13, 18)] + [_, _], "そうさほうほう -> Controls"),
    (0x3D8784, (5, 3), [(5, 13)] * 7, [(5, 13)] * 5 + [_, _], "Controls underline: 5 tiles"),
    (0x3D8784, (4, 20), [(5, 6), (0, 10), (5, 6)], [(0, 18), (1, 16), (1, 17)], "ルール -> Rules"),
    (0x3D8784, (6, 1), [(5, 14), (1, 17), (5, 7), (1, 16), (1, 17), (5, 8), (0, 10)],
     [(5, 14), (1, 18), (2, 16), (2, 17), _, _, _], "[+] じゅうじキー -> D-Pad"),
    (0x3D8784, (9, 1), [(5, 15), (5, 9), (0, 2), (0, 3), (0, 4), _], [(5, 15), (5, 9)] + [(0, c) for c in range(2, 6)],
     "[A] Aボタン -> A Button"),
    (0x3D8784, (12, 1), [(5, 16), (5, 10), (0, 2), (0, 3), (0, 4), _],
     [(5, 16), (5, 10)] + [(0, c) for c in range(2, 6)], "[B] Bボタン -> B Button"),
    (0x3D8784, (15, 1), [(5, 17), (5, 11), (0, 3), (0, 10), (5, 12)], [(5, 17), (2, 18), (5, 5), (5, 6), _],
     "[o] スタート -> Start"),
]


# Fortune box (boot, scene `fortune`; block 0231524, BG1 SCR 0x234034 30x20, words 32 * row + col, palette 2).
# Health け ん こ う (14,1-4) and Study べ ん き ょ う share 14,2 / 14,4, so Study gets its own run; Money gets a 5th
# tile. 14,21-31 are flat, unused tiles (docs/re/graphics.md "Fortune box").
FORTUNE_ROWS = [
    (0x234034, (9, 9), [(14, 5), (14, 6), (14, 2), (14, 7), (14, 8), (14, 4)],
     [(14, 5), (14, 6), (14, 7), (14, 8), (14, 21), _], "fortune べんきょう -> Study"),
    (0x234034, (11, 9), [(14, 9), (14, 10), (14, 11), (14, 12), _],
     [(14, 9), (14, 10), (14, 11), (14, 12), (14, 22)], "fortune おかね -> Money"),
]


def mini_patches(rom, rows=None, tag="minigame"):
    """MAP_PATCHES-style rows for MINI_ROWS (or `rows` of the same form; checks each SCR header and its JP tiles)."""
    out = []
    for off, at, old, new, why in MINI_ROWS if rows is None else rows:
        if rom[off:off + 4] != b"SCR\0":
            raise ValueError(f"{off:#x}: no SCR header ({why})")
        w, h = rom[off + 5], rom[off + 6]
        row, col = at if isinstance(at, tuple) else (at, 0)
        if len(old) != len(new) or col + len(old) > w or row >= h or (col == 0 and len(old) != w and not
                                                                          isinstance(at, tuple)):
            raise ValueError(f"{off:#x} row {row}: {len(old)}/{len(new)} tiles for a {w}x{h} map ({why})")
        e = off + 8 + 2 * (row * w + col)
        words = list(struct.unpack_from(f"<{len(old)}H", rom, e))
        got = [None if v & 0x3FF == 0 else divmod(v & 0x3FF, 32) for v in words]
        if got != old:
            raise ValueError(f"{off:#x} row {row}: JP tiles {got} differ from {old} ({why})")
        # palette bits per word (an icon may use another palette than the text beside it): the tile's own JP word
        # if it was in the row, else the JP word at that place, else the nearest JP tile to the left
        own = {t: v & 0xF000 for t, v in zip(got, words) if t}

        def pal(i, t):
            if t in own:
                return own[t]
            j = next(j for j in list(range(i, -1, -1)) + list(range(i, len(words))) if got[j])
            return words[j] & 0xF000
        out.append((e, words, [0 if t is None else pal(i, t) | (32 * t[0] + t[1]) for i, t in enumerate(new)],
                    f"{tag} {why}"))
    return out


def archive_words(rom):
    """-> {block offset: [ROM offset of each archive word pointing at it]}."""
    n = struct.unpack_from("<I", rom, ARC)[0] // 4
    out = {}
    for i in range(n):
        w = ARC + 4 * i
        out.setdefault(ARC + struct.unpack_from("<I", rom, w)[0], []).append(w)
    return out


def blocks(rom):
    return ecd.scan(rom)


# IMG blocks with no PLT of their own -> an IMG block whose PLT (16 distinct colours) to borrow: only the indices
# matter, the PNG is converted back by colour. 01E9764 (Dyna Customize title etc.) uses PDA OBJ palette 0 in game.
# A PLT that repeats a colour (025E304: red in 1 6 7 8 13-15) would turn a drawn index into another one on the way
# back from PNG, so palette_for nudges each repeat by 1 in blue (real GBA colours are multiples of 8).
PLT_FOR = {0x1E9764: 0x22CF64,
           # field-mode menu titles with no PLT of their own (the screen palette comes from code): same stand-in
           **{o: 0x22CF64 for o in (0x1EA6B4, 0x1EA8C4, 0x1EAA04, 0x1EB9E4, 0x1ECD84, 0x1EE624, 0x1EFFF4,
                                    0x1F4284)}}


def distinct(cols):
    out = []
    for c in cols:
        # the first free blue above, then below (a colour repeated 8+ times, as 0432534's 11 x magenta, used to
        # bounce between 254 and 255 for ever); the upward order keeps the colours of PNGs drawn before
        if c in out:
            c = next((c[0], c[1], b) for b in [*range(c[2] + 1, 256), *range(c[2] - 1, -1, -1)]
                     if (c[0], c[1], b) not in out)
        out.append(c)
    return out


def palette_for(rom, off, bl=None):
    """-> (list of RGB, PLT offset): the first PLT block after IMG block `off` (the game stores them in pairs)."""
    bl = bl or blocks(rom)
    if off in PLT_FOR:
        return palette_for(rom, PLT_FOR[off], bl)
    i = [b[0] for b in bl].index(off)
    for j in range(i + 1, min(i + 4, len(bl))):
        if bl[j][3] == "PLT":
            raw = ecd.decompress(rom, bl[j][0])[0]
            n = struct.unpack_from("<H", raw, 4)[0] or 16
            cols = []
            for k in range(min(n, 16)):
                v = struct.unpack_from("<H", raw, 8 + 2 * k)[0] if 10 + 2 * k <= len(raw) else 0
                cols.append(((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8))
            return distinct(cols), bl[j][0]
    raise ValueError(f"no PLT after {off:07X}")


def indices(raw):
    """IMG payload (4bpp) -> (w px, h px, list of palette indices row-major)."""
    flag, w, h = raw[4], raw[5], raw[6]
    if flag != 0:
        raise ValueError("only 4bpp IMG blocks are handled")
    data = raw[8:]
    W, H = w * 8, h * 8
    px = [0] * (W * H)
    for t in range(w * h):
        tx, ty = t % w, t // w
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                px[(ty * 8 + y) * W + tx * 8 + x] = b >> 4 if x & 1 else b & 15
    return W, H, px


def to_png(raw, pal):
    W, H, px = indices(raw)
    img = Image.new("RGB", (W, H))
    img.putdata([pal[c] if c < len(pal) else (255, 0, 255) for c in px])
    return img


def from_png(path, raw, pal):
    """Edited PNG -> new IMG payload (same header). A colour used by several indices keeps the original pixel's
    index where that colour matches it, else takes the first index with that colour."""
    W, H, orig = indices(raw)
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        raise ValueError(f"{path.name}: {img.size} but the block is {W}x{H}")
    first = {}
    for i, c in enumerate(pal):
        first.setdefault(c, i)
    new = []
    bad = set()
    for k, c in enumerate(img.getdata()):
        o = orig[k]
        if o < len(pal) and pal[o] == c:
            new.append(o)
        elif c in first:
            new.append(first[c])
        else:
            bad.add(c)
            new.append(0)
    if bad:
        raise ValueError(f"{path.name}: colours not in the palette: {sorted(bad)[:6]}")
    w = W // 8
    out = bytearray(raw[:8])
    for t in range((W // 8) * (H // 8)):
        tx, ty = t % w, t // w
        for y in range(8):
            for x in range(0, 8, 2):
                p = (ty * 8 + y) * W + tx * 8 + x
                out.append(new[p] | new[p + 1] << 4)
    out += raw[len(out):]   # trailing bytes past the tiles, if any
    return bytes(out)


def edits():
    return sorted(GFX.glob("[0-9A-F]" * 7 + ".png"))


def apply(rom, out, free, log=None, limit=None):
    """Write every gfx/*.png into `out`. -> next free offset (16-aligned). `rom` = original image."""
    if not edits():
        return free
    title = title_patches(rom) if (GFX / "0449734.png").exists() else []
    title += tt_patches(rom) if (GFX / "022CF64.png").exists() else []
    title += mini_patches(rom) if (GFX / "03D5DB4.png").exists() else []
    title += mini_patches(rom, FORTUNE_ROWS, "fortune") if (GFX / "0231524.png").exists() else []
    title += DATE_PATCHES if (GFX / "021C414.png").exists() else []
    for off, old, new, why in MAP_PATCHES + title:
        if list(struct.unpack_from(f"<{len(old)}H", rom, off)) != old:
            raise ValueError(f"gfx map patch {off:#x}: original words differ ({why})")
        romwrite.put(log, out, off, struct.pack(f"<{len(new)}H", *new), f"gfx map {why}")
    bl = blocks(rom)
    starts = sorted(b[0] for b in bl)
    words = archive_words(rom)
    for path in edits():
        off = int(path.stem, 16)
        raw = ecd.decompress(rom, off)[0]
        pal, _ = palette_for(rom, off, bl)
        new = from_png(path, raw, pal)
        if new == raw:
            continue
        blob = ecd.compress(new)
        nxt = starts[starts.index(off) + 1]
        if len(blob) <= nxt - off:
            romwrite.put(log, out, off, blob, f"gfx {path.stem}")
            continue
        if limit is not None and free + len(blob) > limit:
            raise ValueError(f"gfx {path.stem}: no free space for {len(blob)} bytes")
        romwrite.put(log, out, free, blob, f"gfx {path.stem} (moved)")
        for w in words[off]:
            romwrite.put(log, out, w, struct.pack("<I", free - ARC), f"gfx {path.stem} archive word")
        free = (free + len(blob) + 15) & ~15
    if (GFX / "021C414.png").exists():   # money diary glyph table + the "/" entry (DATE_PATCHES)
        if struct.unpack_from("<I", rom, GLYPHS_PTR)[0] != 0x08000000 + GLYPHS:
            raise ValueError("money diary glyph table pointer differs")
        blob = rom[GLYPHS:GLYPHS + 4 * GLYPHS_N] + struct.pack("<2H", *SLASH)
        if limit is not None and free + len(blob) > limit:
            raise ValueError("money diary glyph table: no free space")
        romwrite.put(log, out, free, blob, "money diary glyph table (moved, + '/')")
        romwrite.put(log, out, GLYPHS_PTR, struct.pack("<I", 0x08000000 + free), "money diary glyph table pointer")
        free = (free + len(blob) + 15) & ~15
    if (GFX / "0432534.png").exists():   # staff roll: its English sprite frames outgrow the old PAT (credits.py)
        import credits
        blob = credits.pat_blob()
        if limit is not None and free + len(blob) > limit:
            raise ValueError(f"credits PAT: no free space for {len(blob)} bytes")
        romwrite.put(log, out, free, blob, "credits PAT (moved)")
        for w in words[credits.PAT]:
            romwrite.put(log, out, w, struct.pack("<I", free - ARC), "credits PAT archive word")
        free = (free + len(blob) + 15) & ~15
    return free


def main(argv):
    rom = ROM.read_bytes()
    if len(argv) >= 2 and argv[0] == "export":
        d = ROOT / "work" / "gfx" / "orig"
        d.mkdir(parents=True, exist_ok=True)
        bl = blocks(rom)
        for a in argv[1:]:
            off = int(a, 16)
            raw = ecd.decompress(rom, off)[0]
            pal, po = palette_for(rom, off, bl)
            img = to_png(raw, pal)
            img.save(d / f"{off:07X}.png")
            img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(d / f"{off:07X}_x4.png")
            print(f"{off:07X}: {img.width}x{img.height}, palette {po:07X}: "
                  + " ".join("%d=%02x%02x%02x" % ((i,) + c) for i, c in enumerate(pal)))
        return 0
    if argv == ["check"]:
        bl = blocks(rom)
        for path in edits():
            off = int(path.stem, 16)
            raw = ecd.decompress(rom, off)[0]
            new = from_png(path, raw, palette_for(rom, off, bl)[0])
            blob = ecd.compress(new)
            print(f"{path.stem}: {'unchanged' if new == raw else 'edited'}, {len(blob)} bytes compressed")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
