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
| Others (cols 2, 3, 7-9, 13, 15, 19, 20, 22) | | 60-96 | guess | measure when a line is LONG |

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

Notes
- The box does not clip: text past x 237 runs over the frame and wraps to the left edge of the map row, so the lint
  must hold every line to its budget.
- Line pieces: the drawer's stack copy holds at most 33 units per piece (docs/re/font.md); a 188 px line needs at
  most 24 units with padding, so this never binds.
