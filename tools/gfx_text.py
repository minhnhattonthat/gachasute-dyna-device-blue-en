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
TT_SUBJECTS = ["Jpn", "Ari", "Sci", "Soc", "Mth", "Eng", "Hlth", "PE",
               "Tec", "HEc", "Crf", "Art", "Mus", "JpH", "WHi", "Geo",
               "Chm", "Phy", "Civ", "Eth", "Bio", None, "Clb", "Act"]
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
                if bits & (0x80 >> gx) for sx in range(k + bold) for sy in range(ky)]
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
    for text, (x0, y0, x1, y1), fill, ink, shadow, font, dy, *own in boxes:
        # ink may be a list: this box's own per-glyph-row gradient (another box may use the same index flat);
        # such a box needs its own clear set
        grad = ink if isinstance(ink, list) else spec.get("grad", {}).get(ink)
        if isinstance(ink, list):
            ink = ink[0]
        kill = own[0] if own else clear.get(ink, {ink})   # optional 8th item: this box's own clear set
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
        ox = x0 + (1 if ring else 0) + (room - w + 1) // 2
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
    return a.image()


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
