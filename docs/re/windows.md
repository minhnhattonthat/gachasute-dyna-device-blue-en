# Window data: width budgets (phase 5 width gate)

Pixel widths are sums of `vwf.width` advances (fonts/vwf8.txt; an SJIS char = 8 px in size-3 cells, 16 in
size 1). Measured in game from zoomed shots; "guess" rows must be measured before a LONG line is cut.

| Variant | Where | Start x | Lines | Budget (px) | Status | Evidence |
|---|---|---|---|---|---|---|
| Message box, portrait | every event message (speaker 1-17) | 48 (map col 6) | 2 per page (a 3rd line never shows) | 188 per line; 176 on a page's last line (the ▼ arrow at x 226-234) | measured | `work/qa/p5_ruler` (40 x H = 200 px runs past the frame, last inner pixel x 237); arrow from `work/qa/warp/intro/hold.png` |
| Message box, no portrait | speaker -1 (926 messages) | 48: same box, a generic emblem in the portrait slot | 2 | as above | measured | `work/qa/p5_ruler2` (build.py --qa s001.00@-1=...) |

Notes
- The box does not clip: text past x 237 runs over the frame and wraps to the left edge of the map row, so the lint
  must hold every line to its budget.
- Line pieces: the drawer's stack copy holds at most 33 units per piece (docs/re/font.md); a 188 px line needs at
  most 24 units with padding, so this never binds.
