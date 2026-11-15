"""gfx_text.py: draw English labels into the game's tile atlases -> gfx/<OFFSET>.png (read by gfx.apply at build).

    python -X utf8 tools/gfx_text.py            # (re)writes every gfx/<OFFSET>.png listed in ATLASES
    python -X utf8 tools/gfx_text.py --zoom     # also work/gfx/en/<OFFSET>_x4.png to look at

An atlas label is a strip of 8x16 px button columns: each column is a (top tile, bottom tile) pair of atlas tiles,
in the order the game's map puts them on screen (docs/re/graphics.md "Field menu bar"). The Japanese ink
(palette index INK) is cleared from rows 2-11 of the strip, then the English is drawn with fonts/vwf8.txt in the
same index, glyph rows 0-6 at strip y 3-9 (descenders at y 10), centred in the strip's text span.
Maps the game reads from ROM data are fixed with gfx.WORD_PATCHES (e.g. a button that used a frame-only tile).
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ecd  # noqa: E402
import gfx  # noqa: E402
import vwf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK = 1
TEXT_Y = 3           # strip row of glyph row 0
CLEAR = range(2, 12)  # strip rows that hold label ink (rows 0-1 and 12-13 are the button frame)


def tiles(row, c0, c1):
    """Atlas tiles (row, c0..c1) as a list."""
    return [(row, c) for c in range(c0, c1 + 1)]


def strip(top, bottom):
    return list(zip(top, bottom))


def mid(tl):
    """A submenu row: blank, 4 middle tiles, blank (the SCR rows' 0x1FF columns)."""
    return [None] + tl + [None]


# Field menu (BG0, block 01E30D4). Bar maps 01E35C4-01E3644: caps 0,0 / 0,5 are blank frame shared by the three
# 6-column buttons, so System/Items/Party draw in their 4 middle columns. Submenu maps 01E3724-01E38A4: 6 tiles a
# row, one 8 px tile tall, the words in atlas rows 2-4; gfx.MAP_PATCHES re-lays rows (Save, Sort, Keywords).
MENU_BAR = 0x1E30D4
# PDA timetable (block 022CF64): 14-row gradient of the f..b lettering, the indices to clear, and the subject cells
# in atlas order (rows 8-13, 8 cells a row; None = keep: HR is Latin already). D15: subject abbreviations.
TT_GRAD = [15, 15, 15, 14, 14, 14, 13, 13, 12, 12, 11, 11, 11, 11]
TT_KILL = {2, 11, 12, 13, 14, 15}
SMALL_GRAD = [15, 15, 14, 14, 13, 12, 11]   # field-mode small words (8 px, no shadow)
SMALL_KILL = {11, 12, 13, 14, 15}
TT_SUBJECTS = ["Jpn", "Ari", "Sci", "Soc", "Mth", "Eng", "Hlth", "PE",
               "Tec", "HEc", "Crf", "Art", "Mus", "JpH", "WHi", "Geo",
               "Chm", "Phy", "Civ", "Eth", "Bio", None, "Clb", "Act"]
# Minigame blocks 03D5DB4 / 03D7FD4: lettering inks and clear sets (big title-style words, HUD words, small charset)
MINI_BIG = {11, 12, 13, 14, 15, 1}
MINI_HUD = [15, 15, 15, 14, 14, 14, 13, 13, 12, 12, 12, 11, 11, 11]
MINI_HUDK = {11, 12, 13, 14, 15, 2}
MINI_SMALL = [15, 14, 14, 13, 13, 12, 12, 12]
MINI_SMALLK = {12, 13, 14, 15}
_S5 = gfx._S5
MINI_WORDS = [("High", _S5[0:3]), ("Score", _S5[3:6]), ("Clear Time", _S5[6:12]), ("New Record!", _S5[12:19]),
              ("Bits Earned", _S5[19:25]), ("Your Bits", _S5[25:30]), ("Give up?", _S5[30:35]), ("Yes", _S5[35:37]),
              ("No", _S5[37:39]), ("Which level?", _S5[39:46]),
              ("", [(3, 0)]), ("", [(3, 1)]), ("s", [(3, 2)]), ("", [(3, 3)]), ("", [(3, 4)]), ("m", [(5, 19)])]
MINI_BOX = {"No": 10}   # "B=No": keep it next to the "=" tile
ATLASES = {
    MENU_BAR: {
        # 1,21 gets the frame-only tile 4,12 (bottom col 1 of a 6-col button) and becomes the Database button's.
        "copy": [((4, 12), (1, 21))],
        "blank": [(2, 4)],   # no longer on any map (Save fits 2,0-2,3)
        "labels": [
            ("System", strip(tiles(0, 1, 4), tiles(1, 1, 4))),
            ("Items", strip(tiles(0, 6, 9), tiles(1, 6, 9))),
            ("Party", strip(tiles(0, 10, 13), tiles(1, 10, 13))),
            ("Residents", strip(tiles(0, 14, 19), tiles(1, 14, 19))),
            ("Database", strip(tiles(0, 20, 23) + [(2, 22), (2, 23)],
                               tiles(1, 20, 23) + [(3, 22), (3, 23)])),
        ],
        "rows": [
            ("Save", mid(tiles(2, 0, 3))),
            ("Battle Anim", tiles(4, 18, 22) + [(3, 20)]),
            ("Quit", mid(tiles(2, 5, 8))),
            ("Use", mid(tiles(2, 9, 12))),
            ("Sort", mid(tiles(2, 14, 17))),
            ("Discard", mid(tiles(2, 19, 21) + [(3, 21)])),
            ("Status", mid(tiles(3, 0, 3))),          # Party and Residents
            ("Equip", mid(tiles(3, 6, 9))),           # Party and Residents
            ("Send Home", tiles(3, 10, 15)),
            ("Release", mid(tiles(3, 16, 19))),       # Party and Residents
            ("Map", mid(tiles(4, 0, 3))),
            ("Dyna", mid(tiles(4, 4, 7))),
            ("Device", mid([(3, 4), (3, 5), (4, 16), (4, 17)])),
            ("Keywords", [(2, 13)] + tiles(4, 8, 11) + [(2, 18)]),
        ],
    },
    # Profile form (BG2, block 020EB44, ink index 4): one-tile-high labels set into the field lines (line at tile
    # y 2, label tiles between 6,29..6,31 frame tiles; tools/bgmap.py on scenes form / form_scroll). The phone
    # labels share their last 3 tiles (ばんごう 8,11-13): "Home" / "Mobile" end flush right, "Tel." starts flush left.
    0x20EB44: {
        "ink": 4,
        "rows": [
            ("Name", tiles(7, 0, 2)),
            ("Nickname", tiles(7, 3, 7)),
            ("Gender", tiles(8, 0, 3)),
            ("Address", tiles(8, 4, 7), "tight"),
            ("Home", tiles(8, 8, 10), "right"),
            ("Tel.", tiles(8, 11, 13), "left"),
            ("Mobile", tiles(8, 14, 17), "right"),
            ("Email", tiles(8, 18, 23)),
            ("Birthday", tiles(8, 24, 28)),
            ("Blood Type", tiles(7, 25, 30)),
        ],
        # Memo / address-book index tabs ア..ワ: BG1 map tiles 0xBC-0xF7 = block tile - 0x80 (scene mode_pda_list,
        # ppu f600), 24 px pitch, ink 15 with drop shadow 14. The tabs share their side tiles (map row 2: bc / c4,
        # row 3: f1 / f2 repeat), so each tab's letter must stay inside its middle tile: romaji initials.
        "screens": [{
            "cells": [[t - 0x80 for t in (0xbc, 0xbd, 0xbe, 0xbf, 0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xbc, 0xc6, 0xc7, 0xc8,
                                          0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xce, 0xcf, 0xc4, 0xbc, 0xd2, 0xc4, 0xbc, 0xd5,
                                          0xc4, 0xbc, 0xd8, 0xc4)],
                      [t - 0x80 for t in range(0xda, 0xf6)][:26] + [0xf1 - 0x80, 0xf2 - 0x80, 0xf6 - 0x80, 0xf7 - 0x80]],
            "redraw": [("", (24 * k + 2, 1, 24 * k + 23, 10), "row", 15, 14, "vwf", 1) for k in range(10)]
                      + [(t, (24 * k + 8, 1, 24 * k + 16, 10), "row", 15, 14, "vwf", 1)
                         for k, t in enumerate("AKSTNHMYRW")],
            "clear": {15: {14, 15}},
        }],
    },
    # PDA home / Dyna Device app labels (OBJ, block 0208654, block tile n = OBJ tile n; white ink 7 on 0, the game
    # adds the dark outline). Scene mode_pda_profile OAM f930: アドレス = 32x8 at tile 5,12; ダイナデバイス = 32x8 +
    # 16x8 at 6,20; データセーブ = 32x8 + 16x8 at 7,8: labels are whole tiles, contiguous on screen. The other app
    # labels (unseen) are taken to be the tile runs their kana cover. おこづかい = おこづか 5,22-25 + い at 3,19.
    0x208654: {
        "ink": 7, "bg": 0,
        "blank": [(3, 19)],   # the い of おこづかい: "Money" fits the four tiles
        "rows": [
            ("Address", tiles(5, 12, 15), "tight"),
            ("Schedule", tiles(5, 16, 21)),
            ("Money", tiles(5, 22, 25)),
            ("Calculator", tiles(6, 0, 4), "tight"),
            ("Timetable", tiles(6, 5, 9), "tight"),
            ("Music", tiles(6, 10, 15)),
            ("Link", tiles(6, 16, 19)),
            ("DynaDevice", tiles(6, 20, 25), "tight"),   # "Dyna Device" is 50 px
            ("Minigame", tiles(7, 0, 4)),
            ("Save Data", tiles(7, 8, 13)),
        ],
        "redraw": [("MEMO", (144, 32, 160, 40), "row", 7, None, "mini", 2, {7})],   # メモ: two tiles
    },
    # PDA home panel headers (block 0206CF4, scene mode_pda_profile): 予定 in the header art x24-47 (ink 2, drop
    # shadow 6 on 4; yellow on grey in game), 用事 as a 3-tile overlay x128-151 y8-23. 24 px each, so 用事 is
    # "To-do" ("Errands" is 32 px).
    0x206CF4: {
        "redraw": [("Plans", (24, 4, 48, 14), "row", 2, 6, "vwf", 0, {2, 6}),
                   ("To-do", (128, 12, 152, 22), "row", 2, 6, "vwf", 0, {2, 6})],
    },
    # PDA Link menu (OBJ, 2D mapping, block 0249C44 = OBJ tile r*32+c; scene pda_link): title つうしんメニュー
    # x16-143 y0-15 (12 px lettering, gradient 15..11, drop shadow 2 on navy 1) -> "Link Menu" in the doubled font.
    # Labels = 8-tile navy bands (lines 2 at tile rows 1 and 6), lettering 8 px tall (gradient, outline 2): row 2
    # c2-9 Item Trade, c10-17 Card Trade, row 3 c2-9 Link Battle (OAM caps 3,10-11 either side), row 4 c0-11
    # Dyna Trade (slanted ends in c0 / c11). The lettered tiles get the blank band tile 3,10, then the English.
    0x249C44: {
        "copy": [((3, 10), t) for t in tiles(2, 2, 17) + tiles(3, 2, 9) + tiles(4, 1, 10)],
        "grad": {15: [15, 15, 15, 14, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11],   # title, doubled rows
                 14: [15, 15, 14, 13, 12, 11, 11, 11]},                        # labels
        "redraw": [("Link Menu", (16, 0, 144, 16), "row", 15, 2, "vwf2", 1, {2, 11, 12, 13, 14, 15}),
                   ("Item Trade", (16, 16, 80, 24), "row", 14, ("ring", 2), "vwf", 0, set()),
                   ("Card Trade", (80, 16, 144, 24), "row", 14, ("ring", 2), "vwf", 0, set()),
                   ("Link Battle", (16, 24, 80, 32), "row", 14, ("ring", 2), "vwf", 0, set()),
                   ("Dyna Trade", (8, 32, 88, 40), "row", 14, ("ring", 2), "vwf", 0, set())],
    },
    # Link connection screen (scenes pda_link_*: every Link menu item opens it without a cable). Headers block
    # 03B3624 (OBJ tile r*32+c): せつぞくかくにん x32-159 y0-15 (shown at x56, orbs either side), ルールせんたく
    # x48-159 y16-31 and バトルアニメせってい x0-159 y32-47 (both need a link partner: unseen). Lettering as the
    # Link menu title (gradient 15..11, drop shadow 2 on navy 1).
    0x3B3624: {
        "grad": {15: [15, 15, 15, 14, 14, 14, 13, 13, 13, 12, 12, 12, 11, 11]},
        "redraw": [("Link Check", (32, 0, 160, 16), "row", 15, 2, "vwf2", 1, {2, 11, 12, 13, 14, 15}),
                   ("Select Rules", (48, 16, 160, 32), "row", 15, 2, "vwf2", 1, {2, 11, 12, 13, 14, 15}),
                   ("Battle Animation", (0, 32, 160, 48), "row", 15, 2, "vwf2", 1, {2, 11, 12, 13, 14, 15})],
    },
    # Link status words, block 03B3164 (BG tiles at VRAM 0x8000 in 32-tile rows: tile r*32+c; BG1 map row 8 cols
    # 10-18 inside the BG2 box): つながっていません = 2,3-10 + 3,10 (red 13, seen); つながっています 1,3-10 (white
    # 15) and せつぞくちゅう 0,4-10 (yellow 14) need a partner (unseen; assumed the same 9-tile slot). Still JP and
    # unseen: シンプル / エキスパート (4,0-9), ２３４Ｐ and the column fragments at x88-103.
    0x3B3164: {
        "ink": 13,
        "rows": [("Not connected", tiles(2, 3, 10) + [(3, 10)])],
        "redraw": [("Connecting...", (32, 0, 88, 8), "row", 14, None, "vwf", 0, {14}),
                   ("Connected", (24, 8, 88, 16), "row", 15, None, "vwf", 0, {15})],
    },
    # PDA Save Data dialog (OBJ, 2D mapping, block 020A4D4, ink 7 on 0; scenes pda_save / pda_saving, ppu dumps).
    # Prompt y76: 5,0-3 x56 | gap | 5,4-7 x96 | gap | 5,8-13 x136. Buttons y92 share 4-tile pieces: left = P Q R
    # (5,14-17 / 18-21 / 22-25) at x16, right = P S T R (5,14-17 / 26-29 / 30 / 22-25) at x120, so P and R are
    # blanked and each button lives in Q or S+T. Saving y76: 0,28-31 + 1,28-31 x88; y92: 2,28-31 + 4,26 x60 | gap |
    # 3,28-31 + 4,27-31 x108. Rows 0-3 cols 0-27 are the blue panel (shared by both states).
    0x20A4D4: {
        "ink": 7,
        "blank": tiles(5, 14, 17) + tiles(5, 22, 25),
        "rows": [
            ("Save", tiles(5, 0, 3), "right"),
            ("all your", tiles(5, 4, 7), "tight"),
            ("data?", tiles(5, 8, 13), "left"),
            ("A: Save", tiles(5, 18, 21), "tight"),
            ("B: Cancel", tiles(5, 26, 30)),
            ("Saving...", tiles(0, 28, 31) + tiles(1, 28, 31)),
            ("Keep", tiles(2, 28, 31) + [(4, 26)], "right"),
            ("the power on.", tiles(3, 28, 31) + tiles(4, 27, 31), "left"),
        ],
    },
    # Profile form popup (OBJ, 2D mapping, block 02124B4, ink 7 on 5): each line is 4-tile sprites with 8 px gaps
    # the OAM leaves between them (scene form, ppu dump f1080): line 1 = 6,19-27 x56 | gap | 6,28-31 + 7,30-31 x136;
    # line 2 = 7,19-22 x32 | gap | 7,23-26 x72 | gap | 8,19-30 x112. Words break at the gaps.
    0x2124B4: {
        "ink": 7, "bg": 5,
        "rows": [
            ("Let's register", tiles(6, 19, 27), "right"),
            ("as a user.", tiles(6, 28, 31) + tiles(7, 30, 31), "left"),
            ("Please", tiles(7, 19, 22), "right"),
            ("enter", tiles(7, 23, 26)),
            ("your details.", tiles(8, 19, 30), "left"),
        ],
        # PDA address book (mode 2), same block: index tabs as the memo's 0225EC4 (identical art); R band
        # アドレスのついか (ink 4, drop shadow 14 on a gradient; copy 2 at x+104, y+1); buttons セレクト (ink 1) +
        # データをけす (ink 4), copy 2 at x+80, y+1. Kana shading 11/12 is cleared with the ink.
        "redraw": [(t, (24 * k + 4, 1, 24 * k + 21, 10), "row", 13, ("ring", 14), "vwf", 1)
                   for k, t in enumerate("AKSTNHMYRW")]
                  + [("Add Address", (33, 21, 97, 30), "row", 4, 14, "vwf", 0, {4, 5, 11, 12, 14}),
                     ("Add Address", (136, 22, 200, 31), "row", 4, 14, "vwf", 0, {4, 5, 11, 12, 14}),
                     ("Select", (3, 101, 29, 110), "row", 1, 14, "vwf", 0),
                     ("Select", (83, 102, 109, 111), "row", 1, 14, "vwf", 0),
                     ("Erase", (30, 101, 77, 110), "row", 4, 14, "vwf", 0),   # "Erase Data" leaves no gap
                     ("Erase", (110, 102, 157, 111), "row", 4, 14, "vwf", 0),
                     # faint delete prompt (ink 7 on 5), JP word spans 5-51 61-90 101-146 / 5-59 77-147; its
                     # screen is not seen yet (the player's own card can't be erased), so sprite gaps are unknown
                     ("Erase this data?", (5, 36, 147, 46), "row", 7, None, "vwf", 1, {7}),
                     ("A: Erase", (5, 50, 60, 60), "row", 7, None, "vwf", 1, {7}),
                     ("B: Keep", (77, 50, 148, 60), "row", 7, None, "vwf", 1, {7})],
        "clear": {13: {13, 14}, 4: {4, 11, 12, 14}, 1: {1, 14}},
    },
    # PDA schedule tabs (block 020B0F4, ink 1): map SCR 0x20BAB4 is 5 buttons of 6 columns like the menu bar,
    # caps 3,0 / 3,5 (4,0 / 4,5) shared, text in the 4 middle columns; the third button's bottom row puts 4,13
    # before 4,12. Original kana at band y 4-10.
    0x20B0F4: {
        "text_y": 4,
        "labels": [
            ("Name", strip(tiles(3, 1, 4), tiles(4, 1, 4))),
            ("Place", strip(tiles(3, 6, 9), tiles(4, 6, 9))),
            ("To Do", strip(tiles(3, 10, 13), [(4, 10), (4, 11), (4, 13), (4, 12)])),
            ("Event", strip(tiles(3, 14, 17), tiles(4, 14, 17))),
            ("Custom", strip(tiles(3, 18, 21), tiles(4, 18, 21))),
        ],
    },
    # PDA calendar L/R header (block 0219CB4, scene mode_pda_calendar): white ink 3 with a full outline 14 on a
    # grey gradient, two copies (the second +112/+104 px right, 1 px lower). Glossary 予定/用事 = Plans/Errands.
    0x219CB4: {
        "redraw": [(t, box, "rowmode", 3, ("ring", 14), "vwf", 1)
                   for t, box in (("Add Plan", (20, 4, 80, 13)), ("Add Plan", (132, 5, 192, 14)),
                                  ("Add Errand", (37, 20, 97, 29)), ("Add Errand", (141, 21, 201, 30)))],
        "clear": {3: {3, 11, 12, 13, 14}},   # 11-13: the kana's shading
    },
    # PDA money diary header (OBJ, block 021EAA4, block tile n = OBJ tile 480 + 32*row + col; scene pda_money,
    # OAM f450 / f900). L band = atlas y0-15 (copy 2 at x+112, same rows: the pressed state), white ink 3 with
    # outline 14 and shading 5/8/12 on a grey gradient; 8 is also a background grey, so it is cleared but still
    # counted in the row's colour ("mode_skip"). The R band (y16-31) has no word of its own: an 8 px overlay strip
    # from y32 sits on it at screen x161-168 (こんげつぶん x0-55, こんしゅうぶん x56-111, もらったお金ついか
    # x112-183, on transparent 0), right of the band's icon and left of its R. Terms as strings t0B9208/18, t0B924C.
    0x21EAA4: {
        "redraw": [(t, box, "rowmode", 3, ("ring", 14), "vwf", 1)
                   for t, box in (("Add Money Out", (12, 4, 80, 13)), ("Add Money Out", (124, 4, 192, 13)))]
                  + [(t, box, "row", 3, ("ring", 14), "vwf", 0)
                     for t, box in (("This Month", (0, 32, 52, 40)), ("This Week", (56, 32, 108, 40)),
                                    ("Add Money In", (112, 32, 174, 40)),
                                    ("", (108, 32, 112, 40)), ("", (174, 32, 184, 40)))],   # kana tails
        "clear": {3: {3, 5, 8, 12, 14}},
        "mode_skip": {3: {3, 5, 12, 14}},
    },
    # PDA calculator (mode 7) + memo R header (OBJ, block 02280B4, OBJ tile 32*row + col at VRAM 0x10000). Button
    # words are separate sprites on transparent 0 laid over the 64 px buttons (OAM f600: やりなおし = atlas
    # x176-223 y32-47 at screen 12,134; 税込み = x176-207 y48-63 at 84,134): blue ink (OBJ pal 2: 1 dark .. 8/7
    # lighter rows) embossed with white 10 below-right; drawn with a row gradient + a white drop shadow. The R band
    # スクロール (two copies, the second 17 rows lower) is outlined white like the calendar header.
    0x2280B4: {
        "redraw": [("Clear", (176, 34, 224, 47), "row", 1, 10, "vwf", 3),
                   ("+Tax", (176, 49, 208, 62), "row", 1, 10, "vwf", 3),
                   ("Scroll", (36, 4, 87, 13), "rowmode", 3, ("ring", 14), "vwf", 1),
                   ("Scroll", (36, 21, 87, 30), "rowmode", 3, ("ring", 14), "vwf", 1)],
        "clear": {1: set(range(1, 16)), 3: {3, 5, 8, 12, 14}},
        "mode_skip": {3: {3, 5, 12, 14}},
        "grad": {1: [1, 1, 6, 6, 4, 8, 7, 7]},
    },
    # PDA memo (mode 6; OBJ, block 0225EC4, 30 tiles wide: block tile 30*row + col = OBJ tile 480 + 32*row + col).
    # R-band overlay strips (OBJ pal 1: white ink 4, outline 14, shading 5/8/12, on transparent 0), shown at screen
    # x160 y5: あたらしく かく x152-215 y48-55, ひともじ けす y56-63. Index tabs ア..ワ (y0-15, 24 px pitch, white 13
    # outlined 14 on tab blue; the selected tab is this OBJ copy, the rest BG) become the kana rows' romaji
    # initials, the order the game sorts by.
    0x225EC4: {
        "redraw": [(t, box, "row", 4, ("ring", 14), "vwf", 0)
                   for t, box in (("New Memo", (150, 48, 216, 56)), ("Backspace", (150, 56, 216, 64)))]
                  + [(t, (24 * k + 4, 1, 24 * k + 21, 10), "row", 13, ("ring", 14), "vwf", 1)
                     for k, t in enumerate("AKSTNHMYRW")],   # as the BG tabs (020EB44 "screens")
        "clear": {4: {4, 5, 8, 12, 14}, 13: {13, 14}},
    },
    # Name-entry keyboard (OBJ, block 020BDD4, block tile n = OBJ tile n; scene keyboard_select, OAM at f1260).
    # Outlined art, so "redraw" boxes (atlas px): the old lettering is cleared and rebuilt from the background,
    # then the English is drawn. Tabs (ink 1, game palette shows it dark): normal tabs x6-31, 9-row pitch from y1;
    # selected tabs x38-63 (かな y0, the rest y16 + 8k). Their background is a per-pixel vote over the 6 tabs of a
    # state. START/SELECT sub-words けってい / へんかん (ink 1, shadow 15): copy C x128-159 is on screen, copies
    # A (x4-37) and B (x43-80) are the pressed states. 前のページ / 次のページ: ink 4, shadow 14.
    0x20BDD4: {
        "redraw": (
            [(t, (8, y, 30, y + 9), "vote:normal", 1, None, "vwf", dy)
             for t, y, dy in (("Hira", 1, 1), ("Kata", 10, 1), ("Sym", 37, 0), ("Kanji", 46, 0))]
            + [(t, (39, y, 63, y + 8), "vote:selected", 1, None, "vwf", dy)
               for t, y, dy in (("Hira", 0, 1), ("Kata", 16, 1), ("Sym", 40, 0), ("Kanji", 48, 0))]
            + [("OK", (125, 51, 157, 58), "row", 1, 15, "mini", 1),
               ("CONVERT", (125, 69, 157, 76), "row", 1, 15, "mini", 1),
               ("OK", (5, 59, 36, 66), "row", 1, 15, "mini", 1),
               ("CONVERT", (5, 78, 36, 85), "row", 1, 15, "mini", 1),
               ("OK", (45, 68, 78, 74), "row", 1, 15, "mini", 0),
               ("CONVERT", (45, 85, 78, 88), "row", 1, 15, "mini", 0),   # cut at row 88 like the original
               ("Prev Page", (177, 36, 232, 46), "row", 4, 14, "vwf", 1),
               ("Next Page", (184, 51, 240, 62), "row", 4, 14, "vwf", 2),
               ("Prev Page", (177, 69, 232, 79), "row", 4, 14, "vwf", 1),
               ("Next Page", (184, 84, 240, 95), "row", 4, 14, "vwf", 2)]),
        "votes": {
            "normal": [(8, 1 + 9 * k) for k in range(6)],
            "selected": [(39, 0)] + [(39, 16 + 8 * k) for k in range(5)],
        },
        "clear": {1: {1, 15}, 4: {4, 14, 12}},
    },
    # Dyna Customize title (mode 13 = scene mode_customize; OBJ 2D, block 01E9764 22 tiles wide, OBJ tile 520 + 32 *
    # row + col; no PLT: gfx.PLT_FOR). ダイナカスタマイズ = r0-1 c2-14 (screen x64-167) then r2-3 c9-13 (x168-207),
    # timetable-logo style: gradient f..b, drop shadow 2 on navy 1.
    0x1E9764: {
        "redraw": [("Customize Dyna", [(16, 0, 120, 16), (72, 16, 112, 32)], "row", TT_GRAD, 2, "vwf2", 1, TT_KILL)],
    },
    # Battle placement (mode 28 = scene mode_placement; OBJ, block 025E304, OBJ tile 32 * row + col). Title
    # ダイナはいち = r0-1 c0-9 (x0-79, three pieces at screen x120): blue gradient 7..11, drop shadow 12, on
    # transparent. Still JP in this block (screens not reached yet): いどう, コマンドせんたく, てきのエリア, もどる,
    # ステータス?, てきエリア (docs/re/graphics.md).
    0x25E304: {
        "redraw": [("Place Dyna", (0, 0, 80, 16), "row", [7, 7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11], 12,
                    "tallb", 1, {7, 8, 9, 10, 11, 12})],
    },
    # Dyna get / naming (mode 45 = scene dyna_new / dyna_name; OBJ 2D, block 0203D14 31 tiles wide, OBJ tile 480 +
    # 32 * row + col). Info panel = PAT 0x204234 frame 2 (frame 1 = labels only): labels タイプ / スタイル / ぞくせい
    # = 32x8 r4 c0-3 / c4-7 / c8-11 (orange gradient 7..3 on transparent); white ink 1 message lines, all from x8:
    # r4 c12-19 | r5 c0-7 | r5 c8-11 | r5 c15-18 + r5 c6 | r5 c19-22 + r4 c21-22. r5 c6 (の) ends lines 2 and 4
    # (x56 / x40), so it and c7 are blanked: line 2 keeps to c0-5, line 4 to c15-18. Naming prompt (7 sprites placed by code, y0): r0 c17-28 then
    # r2 c17-30, one 208 px strip from screen x16 (blue bar x33-207). NEW! art is English already.
    0x203D14: {
        "redraw": [(t, (x, 32, x + 32, 40), "row", [7, 7, 6, 6, 5, 4, 3, 3], None, "vwf", 0, {3, 4, 5, 6, 7}, "left")
                   for t, x in (("Type", 0), ("Style", 32), ("Element", 64))]
                  + [(t, box, "row", 1, None, "vwf", 1, {1}, "left")
                     for t, box in (("This is your", (96, 32, 160, 40)), ("first Dyna", (0, 40, 48, 48)),
                                    ("", (48, 40, 64, 48)), ("of this", (64, 40, 96, 48)),
                                    ("style &", (120, 40, 152, 48)),
                                    ("element!", [(152, 40, 184, 48), (168, 32, 184, 40)]))]
                  + [("Please give this Dyna a name.", [(136, 0, 232, 16), (136, 16, 248, 32)], "row", 1, None,
                      "vwf", 3, {1})],
    },
    # Battle results (mode 36 = scene d_get; OBJ 2D, block 03B9D84 28 tiles wide, OBJ tile 32 * row + col). Header
    # けっか r0-1 c5-10 (x16, timetable-logo style on navy 1); column heads (ink 10, shadow 1, on transparent):
    # いきのこり/ダイナ r0-1 c11-16 at x112, ぜんめつ r0 c17-20 x176 over ターン r1 c17-20 x184 (8 px right),
    # かくとく/ポイント r0-1 c21-24 (unseen); outcome words r4-5: かち c0-5 (fill 1..4, outline 14), まけ c6-11 (8..10,
    # outline 11), ひきわけ c12-17 (2..7, outline 13), shown at x36 / x36 / x42. The big ターン after a turn count
    # (r2-3 c23-26) is blanked: the column head says Turn. Icons, digits and P1/P2/COM are kept.
    0x3B9D84: {
        "redraw": [("Results", (40, 0, 88, 16), "row", TT_GRAD, 2, "tallb", 1, TT_KILL),
                   ("Win", (0, 32, 48, 48), "row", [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4], ("ring", 14), "vwf2",
                    1, {1, 2, 3, 4, 14, 15}),
                   ("Lose", (48, 32, 96, 48), "row", [8, 8, 8, 8, 8, 9, 9, 9, 10, 10, 10, 10, 10, 10], ("ring", 11),
                    "vwf2", 1, {8, 9, 10, 11, 15}),
                   ("Draw", (96, 32, 144, 48), "row", [2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7], ("ring", 13), "vwf2",
                    1, {2, 3, 4, 5, 6, 7, 13, 15}),
                   ("", (184, 16, 216, 32), "row", 14, None, "vwf", 0, {1, 11, 12, 13, 14, 15})]
                  + [("Dyna", (88, 0, 136, 8), "row", 10, 1, "vwf", 0, {1, 10}),
                     ("Left", (88, 8, 136, 16), "row", 10, 1, "vwf", 0, {1, 10})]
                  + [(t, box, "row", 9, 1, "vwf", 0, {1, 9})   # these heads are ink 9
                     for t, box in (("Wipeout", (136, 0, 168, 8)), ("Turn", (136, 8, 160, 16)), ("", (160, 8, 168, 16)),
                                    ("Points", (168, 0, 200, 8)), ("Won", (168, 8, 192, 16)), ("", (192, 8, 200, 16)))],
    },
    # Team setup (mode 33 = scene mode_team). Title チームへんせい: OBJ block 03B29B4 (OBJ tile 32 * row + col),
    # three 32x16 pieces r0-1 c5-16 = atlas x40-135, timetable-logo style. Menu words: BG0 tiles of block 03B25A4
    # (11 tiles wide; white ink 1 on transparent, no shadow), laid out by the raw SCR at 0x3B2854 (12x7, words =
    # 32 * row + col): ついか、いれかえ / はずす / けってい shared 12 kana tiles (r0 c8-10, r1-3 c7-9); gfx.MAP_PATCHES
    # gives each line its own run: Add/Swap 5 tiles, Remove 4, Done 3. HP / Lv (c10 rows 1-2) are kept.
    0x3B29B4: {
        "redraw": [("Team Setup", (40, 0, 136, 16), "row", TT_GRAD, 2, "tallb", 1, TT_KILL)],
    },
    0x3B25A4: {
        "screens": [{"cells": [[8, 9, 10, 18, 19], [20, 29, 30, 31, None], [40, 41, 42, None, None]],
                     "redraw": [("Add/Swap", (0, 0, 40, 8), "row", 1, None, "vwf", 0),
                                ("Remove", (0, 8, 32, 16), "row", 1, None, "vwf", 0),
                                # the trailing space keeps Done 1 px from the edge like the others; the box
                                # spans all 3 tiles so the old kana's right part is cleared too
                                ("Done ", (0, 16, 24, 24), "row", 1, None, "vwf", 0)]}],
    },
    # PDA timetable (mode 8; OBJ 2D, block 022CF64, block tile n = OBJ tile n; scenes mode_pda_calendar2, pda_tt_a).
    # Lettering f..b gradient + drop shadow 2: logo 時間割 x32-95 y0-15 (navy 1), weekday header 月..土 16x16 at
    # x96+16k, palette title 時間割設定パレット x32-175 y16-31. Status line (ink 10, shadow 2, y32-47; PAT frames
    # re-laid by gfx.MAP_PATCHES): weekday 16x16 at x16k, 曜日 x96-119 -> ",", 時間目 x184-223 -> "period", "="
    # and the digits kept. R band ひとつ けす (two frames, x0-103 / x104-207) like the calculator's. Subjects: 32x16
    # cells (icon + one-kanji abbreviation in yellow 15, shadow 1) at rows 8-13 + 委 at x224 y48 -> 2-4 letter
    # abbreviations (D15), HR kept.
    0x22CF64: {
        "paint": [(96, 32, 120, 48, 0), (184, 32, 224, 48, 0)],   # 曜日, 時間目
        "redraw": [("Timetable", (32, 0, 96, 16), "row", TT_GRAD, 2, "tallb", 1, TT_KILL),
                   ("Pick a Subject", (32, 16, 176, 32), "row", TT_GRAD, 2, "vwf2", 1, TT_KILL)]
                  + [(d, (96 + 16 * k, 0, 112 + 16 * k, 16), "row", TT_GRAD, 2, "tall", 1, TT_KILL)
                     for k, d in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))]
                  + [(d, (16 * k, 32, 16 * k + 16, 48), "row", 10, 2, "tall", 0, {10, 2})
                     for k, d in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))]
                  + [(",", (96, 32, 99, 48), "row", 10, None, "tall", 0, {10, 2}),
                     ("period", (184, 32, 211, 48), "row", 10, 2, "tall", 0, {10, 2})]
                  + [("Erase One", (x, 52, x + 54, 62), "rowmode", 3, ("ring", 14), "vwf", 1, {3, 11, 12, 14})
                     for x in (33, 137)]
                  + [(t, (32 * (i % 8) + 16, 64 + 16 * (i // 8) + 2, 32 * (i % 8) + 32, 64 + 16 * (i // 8) + 14),
                      "row", 15, 1, "vwf", 2, {15, 1})
                     for i, t in enumerate(TT_SUBJECTS) if t]
                  + [("Cmt", (240, 50, 256, 62), "row", 15, 1, "vwf", 2, {15, 1})],
        "mode_skip": {3: {3, 11, 12, 14}},
    },
    # Minigames (modes 40-42; BG0, docs/re/graphics.md "Minigames"; tools/gfx.py MINI_ROWS re-lays the SCR maps).
    # Block 03D5DB4 (29 tiles wide, VRAM row stride 32): big words in white f..b gradient + shadow 1 (the game swaps
    # palettes: blue on the title, pink for Game Over), HUD words with shadow 2, and a small 7-row charset (f e e d
    # d c c, no shadow) whose kana tiles carry the small English words (gfx._S5 order); kana the code writes beside
    # numbers become "m" / "s" (00ふん00びょう -> 00m 00s) or blank (0てん -> 0: "0pt" read as "Opt").
    0x3D5DB4: {
        "redraw": [("Game", [(88, 64, 112, 80), (208, 32, 216, 48), (112, 64, 128, 80)], "row", TT_GRAD, 1, "vwf2", 0,
                    MINI_BIG),
                   ("Start", (128, 64, 176, 80), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("", (176, 64, 192, 80), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("Clear", (144, 16, 192, 32), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("Quit", (192, 16, 224, 32), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),   # やめ
                   ("Over", (160, 32, 208, 48), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("", (216, 32, 224, 48), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("Level", (128, 48, 173, 64), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),   # flush left: digit
                   ("", (173, 48, 176, 64), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),        # tiles follow
                   ("Time Up", (0, 64, 72, 80), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("", (72, 64, 88, 80), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   ("Quit", (176, 0, 224, 16), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),     # おわる
                   ("Score", (96, 0, 128, 16), "row", MINI_HUD, 2, "tall", 1, MINI_HUDK),
                   ("Time Left", (128, 0, 176, 16), "row", MINI_HUD, 2, "tall", 1, MINI_HUDK)],
        "screens": [{"cells": [[29 * r + c for r, c in tl]],
                     # clear the whole run first, then draw in a box that may be narrower (flush-left words)
                     "redraw": [("", (0, 0, 8 * len(tl), 8), "row", MINI_SMALL, None, "vwf", 0, MINI_SMALLK),
                                (t, (0, 0, MINI_BOX.get(t, 8 * len(tl)), 8), "row", MINI_SMALL, None, "vwf", 0,
                                 MINI_SMALLK)]}
                    for t, tl in MINI_WORDS],
    },
    # Block 03D7FD4 (19 tiles wide): help header ミニゲーム[1-3]の あそびかた (BG0 rows 1-2: atlas r1-2 c0-9, digit
    # c10-15, の r3-4 c6-7, あそびかた r3-4 c8-18) and the small words of the title R line, the level-select legend
    # and the help page labels (3D8704 / 3D8754 / 3D8784 in gfx.MINI_ROWS).
    0x3D7FD4: {
        "redraw": [("Minigame", (0, 8, 80, 24), "row", TT_GRAD, 1, "vwf2", 0, MINI_BIG),
                   (":", (48, 24, 64, 40), "row", TT_GRAD, 1, "tallb", 1, MINI_BIG),
                   ("How to Play", (64, 24, 152, 40), "row", TT_GRAD, 1, "tallb", 1, MINI_BIG)],
        "screens": [{"cells": [[19 * r + c for r, c in tl]],
                     "redraw": [(t, (0, 0, 8 * len(tl), 8), "row", MINI_SMALL, None, "vwf", 0, MINI_SMALLK)]}
                    for t, tl in (("Button", [(0, 2), (0, 3), (0, 4), (0, 5)]),
                                  ("How to Play", [(0, c) for c in range(6, 13)]),
                                  ("Controls", [(0, c) for c in range(13, 18)]),
                                  ("Rules", [(0, 18), (1, 16), (1, 17)]),
                                  ("D-Pad", [(1, 18), (2, 16), (2, 17)]),
                                  ("Start", [(2, 18), (5, 5), (5, 6)]))],
    },
    # Item shop header (dmode 17 = scene d_item_sell; OBJ 2D at 0x10000, block 01EB9E4 22 tiles wide): ball icon c0-3,
    # アイテムこうにゅう r0-1 c4-21 / アイテムばいきゃく r2-3 c4-21, italic f..b gradient + shadow 2 on navy 1.
    0x1EB9E4: {
        "redraw": [(t, (32, y, 176, y + 16), "row", TT_GRAD, 2, "vwf2", 1, TT_KILL)
                   for t, y in (("Buy Items", 0), ("Sell Items", 16))],
    },
    # Dyna Center headers (OBJ 2D, block 01EAA04 30 tiles wide, same style as 01EB9E4): あずかっている けんちくキット
    # r0-1 c4-29 (dmode 20 = scene d_kit), ダイナのちりょう r2-3 c7-24 between two blue (2) blocks (scene d_dyna_shop).
    0x1EAA04: {
        "redraw": [("Stored Building Kits", (32, 0, 240, 16), "row", TT_GRAD, 2, "vwf2", 1, TT_KILL),
                   # the balls cover the run's ends on screen: keep to the JP glyphs' span
                   ("", (56, 16, 200, 32), "row", TT_GRAD, 2, "vwf2", 1, TT_KILL),
                   ("Treat Dyna", (64, 16, 184, 32), "row", TT_GRAD, 2, "vwf2", 1, TT_KILL)],
    },
    # Item auction + device list (scenes d_auction, d_shop_list; OBJ 2D at 0x10000, block 01ECD84 30 tiles wide, OBJ
    # tile 32 * row + col). Header アイテムオークション = r0-1 c4-13 then r2-3 c4-13 (screen x40-199). Small words
    # r4-6 (8 px, gradient f f e e d c b at y1-7 on transparent) are put together by the code: かいし c6-8 + かかく
    # c9-11, しょじきん r6 c11-15, デバイス r6 c20-23 / アイテム r5 c0-3 + めいしょう r5 c4-8, ぞくせい r5 c12-15,
    # そうびタ r5 c16-19 / ぶそうタ r6 c16-19 + イプ r4 c18-19 (shared: both right-aligned "... Type"). Each piece
    # is its own word so other pairings (げんざい + かかく) still read. Auction, Bid, Bits, Time Left, Current: unseen.
    0x1ECD84: {
        "redraw": [("Item Auction", [(32, 0, 112, 16), (32, 16, 112, 32)], "row", TT_GRAD, 2, "vwf2", 1, TT_KILL)]
        + [(t, box, "row", SMALL_GRAD, None, "vwf", 1, SMALL_KILL, *al) for t, box, *al in (
            ("Auction", (0, 32, 48, 40)), ("Start", (48, 32, 72, 40), "right"), (" Price", (72, 32, 96, 40), "left"),
            ("Bid", (96, 32, 136, 40)),
            ("Item", (0, 40, 32, 48), "right"), (" Name", (32, 40, 72, 48), "left"), ("Bits", (72, 40, 96, 48)),
            ("Element", (96, 40, 128, 48)),
            ("Equip Type", [(128, 40, 160, 48), (144, 32, 160, 40)], "right"),
            ("Arms Type", [(128, 48, 160, 56), (144, 32, 160, 40)], "right"),
            ("Time Left", (0, 48, 48, 56)), ("Current", (48, 48, 80, 56)), ("Funds", (88, 48, 128, 56)),
            ("Device", (160, 48, 192, 56), "right"))],
    },
    # Device development status (scene d_dev_status; same layout, block 01EE624 24 tiles wide): header かいはつ
    # じょうきょう r0-1 / r2-3 c4-13; プロジェクト r4 c0-5 (16 px, gradient + shadow 2), its letter A-D r4 c6-9 is
    # Latin already. Small words r6-7 (もんだいなし, しきんぶそく ...) not seen yet.
    0x1EE624: {
        "redraw": [("Dev. Status", [(32, 0, 112, 16), (32, 16, 112, 32)], "row", TT_GRAD, 2, "vwf2", 1, TT_KILL),
                   ("Project", (0, 32, 48, 48), "row", TT_GRAD, 2, "tall", 2, TT_KILL, "left")],
    },
    # Free battle (scene dbg_colo_free; block 01EFFF4 25 tiles wide): フリーバトル r0-1 c13-24 (screen x72-167; the
    # balls cover the ends, so the narrower tall font).
    0x1EFFF4: {
        "redraw": [("Free Battle", (104, 0, 200, 16), "row", TT_GRAD, 2, "tallb", 1, TT_KILL)],
    },
    # Resident map (scenes dbg_world_map, menu_resident_map; OBJ tile 544 + 32 * row + col, block 01F4284 29 tiles
    # wide): L ズームアウト button r0-1 c11-20, ズームイン R r2-3 c11-20 (dark ink 3 with 4 shading on a 5-8
    # gradient); すんでいる r4 c11-15 + ダイナ c16-18 (shown as one 64 px label), デバイス c19-22, flat ink 12.
    0x1F4284: {
        "redraw": [("Zoom Out", (102, 2, 160, 12), "row", 3, None, "vwf", 1, {3, 4}),
                   ("Zoom In", (104, 18, 150, 28), "row", 3, None, "vwf", 1, {3, 4})]
        + [(t, box, "row", 12, None, "vwf", 1, {12}, "left") for t, box in (
            ("Resident", (88, 32, 128, 40)), ("Dyna", (128, 32, 152, 40)), ("Devices", (152, 32, 184, 40)))],
    },
    # Fortune box (boot with a save, scene `fortune`; BG1, block 0231524 32 tiles wide): きょうの うんせい r13 c12-21,
    # labels r14 after their icon tiles (c0 / c5 / c9 / c13), ink 1, 7 rows at tile y0, no shadow. gfx.FORTUNE_ROWS
    # gives Study c6-8 + c21 and Money c10-12 + c22; Health c1-4 and Lucky Dyna c14-20 stay where they were.
    0x231524: {
        "screens": [{"cells": [[32 * r + c for r, c in tl]],
                     "redraw": [(t, (0, 0, 8 * len(tl), 8), "row", 1, None, "vwf", 0, {1}, align)]}
                    for t, tl, align in (("Today's Fortune", tiles(13, 12, 21), "centre"),
                                         ("Health", tiles(14, 1, 4), "left"),
                                         ("Study", tiles(14, 6, 8) + [(14, 21)], "left"),
                                         ("Money", tiles(14, 10, 12) + [(14, 22)], "left"),
                                         ("Lucky Dyna", tiles(14, 14, 20), "left"))],
    },
    # Title screen (OBJ 2D, block 0449734, block tile n = OBJ tile n; scene mode_title). The logo stays JP (D5).
    # Copyright (rows 12-13 c0-12, screen x68 y140) and the blinking スタートボタンを おしてください (r12-13 c13-28,
    # four 32x16 at x57 y123) are 7-row strokes in ink 5, side neighbours 3, corners 4, on transparent 0. The
    # emblem label エンブレム is the strip r12 c30-31 + r13 c29-31 (screen x72-111 y102; r12 c29 = the bar's cap),
    # white 15 on bar blue 2. Planet names: tools/gfx.py TITLE_NAMES (rows 10-11 repainted, one run per name).
    0x449734: {
        # each bar: n tiles of blue 2, the JP bars' end corners 3 4 at its top and bottom rows
        "paint": [(0, 80, 256, 96, 0)] + [r for _, _, row, col, n in gfx.TITLE_NAMES for r in (
            (8 * col, 8 * row, 8 * (col + n), 8 * row + 8, 2),
            *[(8 * (col + n) - 2 + i, 8 * row + y, 8 * (col + n) - 1 + i, 8 * row + y + 1, 3 + i)
              for i in (0, 1) for y in (0, 7)])],
        "redraw": [("SMILESOFT", (40, 103, 104, 112), "row", 5, ("ring2", 3, 4), "vwf", 1),
                   ("PRESS START", (104, 103, 232, 112), "row", 5, ("ring2", 3, 4), "vwf", 1)]
                  + [(name, (8 * col, 8 * row, 8 * (col + n) - 2, 8 * row + 8), "row", 15, None, "vwf", 0,
                      set()) for _, name, row, col, n in gfx.TITLE_NAMES],
        "clear": {5: {2, 3, 4, 5}},
        "screens": [{"cells": [[414, 415, 445, 446, 447]],
                     "redraw": [("Emblem", (0, 0, 40, 8), "row", 15, None, "vwf", 0)], "clear": {15: {15}}}],
    },
}

# 3x5 caps for the small sub-labels under START / SELECT (N is 4 wide).
MINI = {
    "C": ["###", "#..", "#..", "#..", "###"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "M": ["#.#", "###", "###", "#.#", "#.#"],
}


def glyph_pixels(text, font):
    """[(x, y)] ink pixels of `text` from x 0, and its width."""
    out, x = [], 0
    if font == "mini":
        for ch in text:
            g = MINI[ch]
            out += [(x + gx, gy) for gy, row in enumerate(g) for gx, c in enumerate(row) if c == "#"]
            x += len(g[0]) + 1
        return out, x - 1
    f = vwf.font()
    # "vwf2": every font pixel doubled, for big title lettering; "tall": rows doubled only (14 px high at the
    # 8 px font's width), "tallb": tall and one px bolder (each pixel also drawn one to the right)
    k = 2 if font == "vwf2" else 1
    ky = 2 if font in ("vwf2", "tall", "tallb") else 1
    bold = 1 if font == "tallb" else 0
    for ch in text:
        adv, rows = f[ch]
        out += [(x + k * gx + sx, ky * gy + sy) for gy, bits in enumerate(rows) for gx in range(adv - 1)
                if bits & (0x80 >> gx) for sx in range(k) for sy in range(ky)]
        if bold:   # smear right, but keep 1 px counters open (m, w): only where the next 2 columns are empty
            out += [(x + gx + 1, ky * gy + sy) for gy, bits in enumerate(rows) for gx in range(adv - 1)
                    if bits & (0x80 >> gx) and not bits & (0x80 >> (gx + 1)) and not bits & (0x80 >> (gx + 2))
                    for sy in range(ky)]
        x += k * adv + 2 * bold   # bold: the smear fills the font's 1 px gap, so add 2
    out = sorted(set(out))
    return out, x - k


def redraw(a, spec):
    """Outlined labels: clear the old lettering in each box, rebuild the background, draw the English."""
    clear = spec.get("clear", {})
    boxes = spec["redraw"]
    vote_bg = {}
    for name, origins in spec.get("votes", {}).items():
        x0, y0, x1, y1 = next(b for _, b, f, *_ in boxes if f == "vote:" + name)
        ink = next(i for _, _, f, i, *_ in boxes if f == "vote:" + name)
        bg = {}
        for dy in range(y1 - y0):
            for dx in range(x1 - x0):
                vals = [a.px[(oy + dy) * a.W + ox + dx] for ox, oy in origins]
                vals = [v for v in vals if v not in clear.get(ink, {ink})] or vals
                bg[dx, dy] = max(set(vals), key=vals.count)
        vote_bg[name] = bg
    for item in boxes:
        if isinstance(item[1], list):   # segments: atlas boxes of one height shown side by side on screen
            segs = item[1]
            h = segs[0][3] - segs[0][1]
            strip = type("Strip", (), {})()
            strip.W = sum(x1 - x0 for x0, _, x1, _ in segs)
            strip.px = [0] * (strip.W * h)
            ox = 0
            for x0, y0, x1, y1 in segs:
                for y in range(h):
                    for x in range(x0, x1):
                        strip.px[y * strip.W + ox + x - x0] = a.px[(y0 + y) * a.W + x]
                ox += x1 - x0
            redraw(strip, {**spec, "redraw": [(item[0], (0, 0, strip.W, h)) + tuple(item[2:])], "votes": {}})
            ox = 0
            for x0, y0, x1, y1 in segs:
                for y in range(h):
                    for x in range(x0, x1):
                        a.px[(y0 + y) * a.W + x] = strip.px[y * strip.W + ox + x - x0]
                ox += x1 - x0
            continue
        text, (x0, y0, x1, y1), fill, ink, shadow, font, dy, *own = item
        # ink may be a list: this box's own per-glyph-row gradient (another box may use the same index flat);
        # such a box needs its own clear set
        grad = ink if isinstance(ink, list) else spec.get("grad", {}).get(ink)
        if isinstance(ink, list):
            ink = ink[0]
        # optional 8th item: this box's own clear set (None = the spec's); 9th: "left" = start 1 px into the box,
        # "right" = end at the box's right edge (less the shadow)
        kill = own[0] if own and own[0] is not None else clear.get(ink, {ink})
        left = len(own) > 1 and own[1] == "left"
        right = len(own) > 1 and own[1] == "right"
        if fill.startswith("vote:"):
            bg = vote_bg[fill[5:]]
            for y in range(y0, y1):
                for x in range(x0, x1):
                    a.px[y * a.W + x] = bg[x - x0, y - y0]
        else:   # row: each lettering pixel takes its nearest non-lettering neighbour in the row
            for y in range(y0, y1):
                row = [a.px[y * a.W + x] for x in range(x0, x1)]
                keep = [i for i, v in enumerate(row) if v not in kill]
                if not keep:
                    continue
                skip = spec.get("mode_skip", {}).get(ink, kill)
                kept = [v for v in row if v not in skip]
                common = max(set(kept), key=kept.count)   # "rowmode": a vertical gradient, one colour a row
                for i, v in enumerate(row):
                    if v in kill:
                        j = min(keep, key=lambda k: (abs(k - i), k))
                        a.px[y * a.W + x0 + i] = common if fill == "rowmode" else row[j]
        pix, w = glyph_pixels(text, font)
        ring = isinstance(shadow, tuple)   # ("ring", index): an 8-neighbour outline instead of a drop shadow
        room = x1 - x0 - (2 if ring else 1 if shadow is not None else 0)
        if w > room + (1 if shadow is not None and not ring else 0):   # a drop shadow may be clipped at the right
            raise ValueError(f"{text!r} is {w} px, box {x0}-{x1} holds {room}")
        ox = x0 + (1 if ring else 0) + (1 if left else room - w if right else (room - w + 1) // 2)
        oy = y0 + dy
        ink_at = {(ox + px_, oy + py) for px_, py in pix}
        if ring and shadow[0] == "ring2":   # ("ring2", orth, diag): side neighbours one colour, corners another
            for (sx, sy), col in [((sx, sy), shadow[2]) for sx in (-1, 1) for sy in (-1, 1)] + \
                                 [(o, shadow[1]) for o in ((-1, 0), (1, 0), (0, -1), (0, 1))]:
                for x, y in ink_at:
                    p = (x + sx, y + sy)
                    if p not in ink_at and x0 <= p[0] < x1 and y0 <= p[1] < y1:
                        a.px[p[1] * a.W + p[0]] = col
            shadow = None
        elif ring:
            shadow = shadow[1]
        if shadow is not None:
            offsets = ([(sx, sy) for sx in (-1, 0, 1) for sy in (-1, 0, 1) if sx or sy] if ring
                       else ((1, 0), (0, 1), (1, 1)))
            for x, y in ink_at:
                for sx, sy in offsets:
                    p = (x + sx, y + sy)
                    if p not in ink_at and x0 <= p[0] < x1 and y0 <= p[1] < y1:
                        a.px[p[1] * a.W + p[0]] = shadow
        for x, y in ink_at:   # grad: per glyph row inks, for lettering with a vertical gradient
            if y < y1:
                a.px[y * a.W + x] = grad[min(y - oy, len(grad) - 1)] if grad else ink


class Atlas:
    def __init__(self, rom, off):
        self.raw = ecd.decompress(rom, off)[0]
        self.pal, _ = gfx.palette_for(rom, off)
        self.W, self.H, self.px = gfx.indices(self.raw)

    def get(self, t, x, y):
        r, c = t
        return self.px[(r * 8 + y) * self.W + c * 8 + x]

    def set(self, t, x, y, v):
        r, c = t
        if (r + 1) * 8 > self.H or (c + 1) * 8 > self.W:
            raise ValueError(f"tile {t} outside the {self.W}x{self.H} atlas")
        self.px[(r * 8 + y) * self.W + c * 8 + x] = v

    def copy(self, src, dst):
        for y in range(8):
            for x in range(8):
                self.set(dst, x, y, self.get(src, x, y))

    def image(self):
        img = Image.new("RGB", (self.W, self.H))
        img.putdata([self.pal[c] for c in self.px])
        return img


def strip_cell(columns, x, y):
    """Strip pixel (x, y) -> (tile, tile x, tile y)."""
    top, bottom = columns[x // 8]
    return (top if y < 8 else bottom), x % 8, y % 8


def clear_strip(atlas, columns):
    for y in CLEAR:
        for x in range(len(columns) * 8):
            t, tx, ty = strip_cell(columns, x, y)
            if atlas.get(t, tx, ty) == INK:
                atlas.set(t, tx, ty, 0)


def draw_text(atlas, text, w, top, cell, align="centre", ink=INK):
    """Draw `text` in a span `w` px wide (1 px margin each side; "left"/"right" hug that margin, for a word that
    continues in the next span); cell(x, y) -> (tile, tx, ty) or raises for a blank column."""
    tw = vwf.width(text) - 1
    room = w if align == "tight" else w - 2   # "tight": no margin, for a label set off by a gap in its frame
    if tw > room:
        raise ValueError(f"{text!r} is {tw} px, the label holds {room}")
    x = {"left": 1, "right": w - 1 - tw, "tight": (w - tw) // 2}.get(align, (w - tw + 1) // 2)
    font = vwf.font()
    for ch in text:
        adv, rows = font[ch]
        for gy, bits in enumerate(rows):
            for gx in range(adv - 1):
                if bits & (0x80 >> gx):
                    t, tx, ty = cell(x + gx, top + gy)
                    atlas.set(t, tx, ty, ink)
        x += adv


def row_cell(text, columns):
    def cell(x, y):
        t = columns[x // 8]
        if t is None:
            raise ValueError(f"{text!r} reaches blank column {x // 8} of its row")
        return t, x % 8, y
    return cell


def render(rom, off):
    spec = ATLASES[off]
    a = Atlas(rom, off)
    for src, dst in spec.get("copy", []):
        a.copy(src, dst)
    # clear every label's tiles before drawing any: a freed tile can move to another label (2,13 -> Keywords)
    for t in spec.get("blank", []):
        for y in range(8):
            for x in range(8):
                a.set(t, x, y, 0)
    for x0, y0, x1, y1, col in spec.get("paint", []):   # plain rectangles, before any text
        for y in range(y0, y1):
            for x in range(x0, x1):
                a.px[y * a.W + x] = col
    ink, bg = spec.get("ink", INK), spec.get("bg", 0)
    for _, columns in spec.get("labels", []):
        clear_strip(a, columns)
    for _, columns, *_ in spec.get("rows", []):
        for t in filter(None, columns):
            for y in range(8):
                for x in range(8):
                    if a.get(t, x, y) == ink:
                        a.set(t, x, y, bg)
    for text, columns in spec.get("labels", []):
        draw_text(a, text, len(columns) * 8, spec.get("text_y", TEXT_Y), lambda x, y, c=columns: strip_cell(c, x, y))
    for text, columns, *align in spec.get("rows", []):   # caps rows 0-6, descenders row 7
        draw_text(a, text, len(columns) * 8, 0, row_cell(text, columns), *(align or ["centre"]), ink=ink)
    if "redraw" in spec:
        redraw(a, spec)
    for scr in spec.get("screens", []):
        screen_redraw(a, scr)
    img = a.image()
    # gfx.from_png maps colours back to indices: a palette that repeats a colour would turn a drawn index into
    # another one (025E304: pale 7 came back as navy 1). Fail here instead of in game; fix with gfx.PLT_FOR.
    orig = gfx.indices(a.raw)[2]
    back = lambda v, o: o if a.pal[o] == a.pal[v] else a.pal.index(a.pal[v])   # what gfx.from_png reads
    bad = {(v, o) for v, o in zip(a.px, orig) if back(v, o) != v}
    if bad:
        raise ValueError(f"{off:07X}: drawn indices {sorted(bad)[:4]} (new, old) share a colour with a lower index "
                         "in the block's palette: add the block to gfx.PLT_FOR")
    return img


class Strip:
    """Atlas tiles laid out as the game's BG map shows them: rows of block tile numbers (None = not this block)."""
    def __init__(self, atlas, cells):
        self.cells, self.W, self.H = cells, 8 * len(cells[0]), 8 * len(cells)
        cols = atlas.W // 8
        self.px = [0] * (self.W * self.H)
        for r, row in enumerate(cells):
            for c, n in enumerate(row):
                if n is not None:
                    for y in range(8):
                        for x in range(8):
                            self.px[(8 * r + y) * self.W + 8 * c + x] = atlas.get(divmod(n, cols), x, y)


def screen_redraw(a, scr):
    """`redraw` boxes in screen coordinates of a map strip; tiles the map repeats must come out the same."""
    s = Strip(a, scr["cells"])
    redraw(s, scr)
    cols = a.W // 8
    done = {}
    for r, row in enumerate(s.cells):
        for c, n in enumerate(row):
            if n is None:
                continue
            tile = [s.px[(8 * r + y) * s.W + 8 * c + x] for y in range(8) for x in range(8)]
            if done.setdefault(n, tile) != tile:
                raise ValueError(f"tile {n} repeats on the map but its cells now differ (cell {r},{c})")
            for i, v in enumerate(tile):
                a.set(divmod(n, cols), i % 8, i // 8, v)


def main(argv):
    rom = gfx.ROM.read_bytes()
    gfx.GFX.mkdir(exist_ok=True)
    for off in ATLASES:
        img = render(rom, off)
        path = gfx.GFX / f"{off:07X}.png"
        img.save(path)
        spec = ATLASES[off]
        print(f"{path.relative_to(ROOT)}: {len(spec.get('labels', [])) + len(spec.get('rows', []))} labels")
        if "--zoom" in argv:
            z = ROOT / "work" / "gfx" / "en"
            z.mkdir(parents=True, exist_ok=True)
            img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(z / f"{off:07X}_x4.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
