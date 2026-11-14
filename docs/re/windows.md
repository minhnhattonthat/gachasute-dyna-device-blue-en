# Window data: width budgets (phase 5 width gate)

Pixel widths are sums of `vwf.width` advances (fonts/vwf8.txt; an SJIS char = 8 px in size-3 cells, 16 in
size 1). Measured in game from zoomed shots; "guess" rows must be measured before a LONG line is cut.

| Variant | Where | Start x | Lines | Budget (px) | Status | Evidence |
|---|---|---|---|---|---|---|
| Message box, portrait | every event message (speaker 1-17) | 48 (map col 6) | 2 per page (a 3rd line never shows) | 188 per line; 176 on a page's last line (the ▼ arrow at x 226-234) | measured | `work/qa/p5_ruler` (40 x H = 200 px runs past the frame, last inner pixel x 237); arrow from `work/qa/warp/intro/hold.png` |
| Message box, no portrait | speaker -1 (926 messages) | 48: same box, a generic emblem in the portrait slot | 2 | as above | measured | `work/qa/p5_ruler2` (build.py --qa s001.00@-1=...) |

## String windows (string region 0x0AF6D0-0x0BB7C0)

Source of truth: `tools/budgets.py` (WINDOW table by size and start column, CLASSES by id range) writes
`docs/re/budgets.tsv`; a test keeps it current. Placements: `docs/re/marks_p5.tsv` = `tools/marks.py --tsv` over
the full marker tour (147/147 scenes on `build.py --marker`, 2026-11-15: 153 strings and 252 messages drawn; every
message at the standard box, col 6 row 16). Measured with `tools/edge.py` (a vertical frame line right of the
start) or a zoomed crop of `work/qa/p5_mk/<scene>/hold.png`.

| Window | Start | Budget | Status | Where |
|---|---|---|---|---|
| Description box (4 lines: type, category, 2 text lines) | col 1, x 8 | 88 px (frame x 98) | measured (menu_items, mode_item_sell, d_shop_list, menu_db_keyword_help) | item/device records 0x0BDAE8 (4 pointers per item) |
| Name lists | col 4 / 6 | 64 px | measured (party status attacks: frame x 99; auction: upgrade mark at col 14) | the tightest list: every name class gets 64 |
| Sell list names | col 16 | 80 px (price at x 213) | measured | |
| Item menu list | col 17 | 70 px (count at x 209) | measured | |
| Kit / keyword / dyna status list | col 18 | 70 px (kit count at col 27) | measured | keyword list alone runs to the screen edge (96) |
| Shop list spec panel | col 21 | 66 px (frame x 236) | measured | |
| Customize tree | col 5 | 88 px (frame x 133) | measured | |
| Field build menu / team help / PDA cells | col 2 | 86 px (menu box inner x 104) | measured (`work/qa/g_field`, f24975) | |
| Customize tree, deep level | col 3 | 104 px (frame x 133) | measured | |
| Dyna card HP / mood | col 7 | 58 px (card inner x 114) | measured (mode_dyna_shop) | TRACK label 48, battle result name 74 (ID_WINDOW) |
| Resident map sector label | col 8 | 50 px (panel inner x 114) | measured | date prompt line t0B9944: 141 (box inner x 205) |
| Field menu header: sector type | col 9 | 32 px (box inner x 104) | measured (`work/qa/g_tut` f21995) | all sector type names get 32 |
| Customize level value | col 13 | 28 px (tree frame x 133) | measured | tutorial team card name: 70 (Lv at x 176) |
| Dynapad title | col 15 | 72 px (screen inner x 192) | measured | keyword number 24, money line 114, spec panel 112 |
| Card exchange / free-battle opponent | col 19 | 86 px (inner x 238) | measured (mode_card2, dbg_colo_free) | |
| Resident postal line, party equip names | col 20 | 65 px (frame x 225-226) | measured | |
| Get screen type panel, Dyna status | col 22 | 60 px (inner x 236) | measured (`work/qa/g_tut` f9875) | |
| Keyword help box | col 1 | 100 px (inner x 111) | measured (`work/qa/help12`: a 12-char JP line fits) | keyword/style class 0x0B562C-0x0B802C: 96 (keyword list col 18 to the screen edge) |

Per-id exceptions (one column, different windows) are `ID_WINDOW` in tools/budgets.py. Still **guess** (strings
no tour drew; a LONG line against them means warp there and measure): ヨロシク仮面 0x0AF6D0, PDA places / event
types 0x0B4A70-0x0B4CA8 (60, kanji 銀行 クラブ活動..., probably the PDA schedule entries), and 459 undrawn UI
strings 0x0B8044+ (popups, confirmations, link mode, minigames) at 88.

Findings
- **Wide markers can't tour this game**: `--marker-px 240` on every string hangs the profile form (a size-1 date
  field t0B98C4 gets 35 units of 16 px cells), and on dense screens long strings overwrite neighbouring tile
  areas (mode_dyna_status turns to garbage). `--marker-ids TSV` widens only size-3 ids seen in a tour; even then
  the dmode/menu warps fail (their tutorial replay ends off the city road). Measure from the JP-width marker shots.
- String windows don't clip either: wide text runs over frames and wraps at the map row.
- List names are drawn through format strings (`{%sR0}`-style, e.g. t0B9F44 in the keyword list): the name's
  window is the format's position.
- Description lines are 88 px against a JP maximum of 11 full-width chars (88 px): English gets about 14-16
  characters per line. Engine work (a 4x6 font or a wider box) is the fix if that proves too tight in phase 6.

## String registers (`{%sRn}`; lint.REG_PX, measured 2026-11-15)

A register is 8 bytes at 0x02002BD4 + 8n: u32 pointer (or number) + u32 type; the expander copies the pointed
string (probe `tools/lua/regprobe.lua`, runs `work/qa/regs/x002` etc.). The register number does not fix the
kind: each script loads its own (R4 = player nickname in 350 messages, but an NPC in s465; R3 = player in s341).
Every value is a name:

| Value | Source | Max | Width |
|---|---|---|---|
| Player nickname | form keyboard -> 0x0200A744 (16 bytes + NUL) | 8 chars (`work/qa/kbmax`: 24 presses -> 8) | 8 x 8 = 64 px full-width |
| Player name (form only) | form keyboard | 12 chars | not in messages |
| Dyna name (R5, R6 ...) | Dyna record 0x48 bytes from 0x02003362, name field 16 bytes + NUL (`work/qa/dyna`) | 8 chars | 64 px |
| Species, item, NPC, type/style/attribute names | ROM strings (R0 ナビュウ 0x0B990C, R1 ケンタウルス 0x0B3AA8) | their own budget | name lists: 64 px |

So **every `%sRn` = 64 px** (`lint.REG_PX["s"]`), measured. Phase 7 rules that keep it true: the English name
keyboard keeps the 8-character limit (8 ASCII letters <= 48 px; full-width Latin, 64 px, still fits), and English
species names (the default Dyna names, copied into the 16-byte field) stay <= 64 px and <= 16 bytes. Open: R5 in
s465-s480 / s589 reads like an activity or goal (`{%sR5}していた`); its table is not found yet, so it gets the
same 64 px as a name. Number registers: `%dRn` 8 px per digit (SJIS digits), `%02dRn` 16 px.

Notes
- The box does not clip: text past x 237 runs over the frame and wraps to the left edge of the map row, so the lint
  must hold every line to its budget.
- Line pieces: the drawer's stack copy holds at most 33 units per piece (docs/re/font.md); a 188 px line needs at
  most 24 units with padding, so this never binds.
